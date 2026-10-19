import base64
import io
import json
from http.server import BaseHTTPRequestHandler
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from urllib.parse import urlparse, parse_qs


DATA_PATH = Path(__file__).resolve().parent.parent / "rotten_tomatoes_movies.csv"


def image_to_base64(fig):
    buffer = io.BytesIO()
    fig.savefig(buffer, format="png", bbox_inches="tight")
    plt.close(fig)
    buffer.seek(0)
    return base64.b64encode(buffer.read()).decode("ascii")


def analyze(movie_title, chosen_genre):
    if not DATA_PATH.exists():
        raise FileNotFoundError(
            "rotten_tomatoes_movies.csv was not found. Add the CSV to the repository root."
        )

    movie_data = pd.read_csv(DATA_PATH)

    required_columns = {
        "movie_title", "year", "critic_rating", "audience_rating", "genres"
    }
    missing = required_columns.difference(movie_data.columns)
    if missing:
        raise ValueError("The CSV is missing required columns: " + ", ".join(sorted(missing)))

    movie_matches = movie_data[movie_data["movie_title"].astype(str).str.casefold() == movie_title.casefold()]
    if movie_matches.empty:
        raise ValueError(f'Could not find "{movie_title}" in the movie dataset. Check the spelling.')
    favorite = movie_matches.iloc[0]

    if pd.isna(favorite["audience_rating"]):
        raise ValueError(f'"{movie_title}" does not have an audience rating in the dataset.')

    genre_matches = movie_data["genres"].fillna("").astype(str).str.contains(
        chosen_genre, case=False, regex=False
    )
    genre_movies = movie_data.loc[genre_matches].copy()
    if genre_movies.empty:
        raise ValueError(f'No movies were found for the genre "{chosen_genre}".')

    ratings = pd.to_numeric(genre_movies["audience_rating"], errors="coerce").dropna()
    if ratings.empty:
        raise ValueError(f'There are no audience ratings available for "{chosen_genre}" movies.')

    favorite_rating = float(favorite["audience_rating"])
    minimum = float(ratings.min())
    maximum = float(ratings.max())
    mean = round(float(ratings.mean()), 1)
    median = float(ratings.median())

    stats = [
        f"The minimum audience rating in this genre is: {minimum:g}",
        f'{movie_title} is rated {favorite_rating - minimum:g} points higher than the lowest-rated movie.',
        f"The maximum audience rating in this genre is: {maximum:g}",
        f'{movie_title} is rated {maximum - favorite_rating:g} points lower than the highest-rated movie.',
        f"The mean audience rating in this genre is: {mean:g}",
    ]

    if favorite_rating > mean:
        stats.append(f"{movie_title} is rated {favorite_rating - mean:.2f} points higher than the mean movie rating.")
    elif favorite_rating < mean:
        stats.append(f"{movie_title} is rated {mean - favorite_rating:.2f} points lower than the mean movie rating.")
    else:
        stats.append("The rating and mean are equal.")

    stats.append(f"The median audience rating in this genre is: {median:g}")
    if favorite_rating > median:
        stats.append(f"{movie_title} is rated {favorite_rating - median:g} points higher than the median movie rating.")
    elif favorite_rating < median:
        stats.append(f"{movie_title} is rated {median - favorite_rating:g} points lower than the median movie rating.")
    else:
        stats.append("The rating and median are equal.")

    fig, ax = plt.subplots()
    counts, bins, _ = ax.hist(ratings, bins=20, range=(0, 100))
    ax.grid(True)
    ax.set_title(f"Audience Ratings of {chosen_genre} Movies")
    ax.set_xlabel("Audience Ratings")
    ax.set_ylabel(f"Number of {chosen_genre} Movies")
    max_index = int(counts.argmax())
    bin_start, bin_end = bins[max_index], bins[max_index + 1]
    histogram_interpretation = (
        "According to the histogram, most movies in this genre fall between a rating of "
        f"{int(bin_start)}–{int(bin_end)}."
    )
    histogram_image = image_to_base64(fig)

    scatter_data = genre_movies[["audience_rating", "critic_rating"]].apply(
        pd.to_numeric, errors="coerce"
    ).dropna()
    if len(scatter_data) >= 2 and scatter_data["audience_rating"].nunique() > 1 and scatter_data["critic_rating"].nunique() > 1:
        corr = round(float(scatter_data["audience_rating"].corr(scatter_data["critic_rating"])), 2)
    else:
        corr = None

    if corr is None:
        relationship = "could not be determined from the available data"
        correlation_interpretation = "Correlation " + relationship + "."
    else:
        if corr > 0.3:
            relationship = "a positive"
        elif corr < -0.3:
            relationship = "a negative"
        else:
            relationship = "no"
        correlation_interpretation = (
            "According to the scatter plot, there is " + relationship +
            " correlation between audience ratings and critic ratings "
            f"(correlation = {corr})."
        )

    fig, ax = plt.subplots()
    ax.scatter(scatter_data["audience_rating"], scatter_data["critic_rating"])
    ax.grid(True)
    ax.set_title("Audience Rating vs. Critic Rating")
    ax.set_xlabel("Audience Rating")
    ax.set_ylabel("Critic Rating")
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    scatterplot_image = image_to_base64(fig)

    def safe_value(value):
        return None if pd.isna(value) else value.item() if hasattr(value, "item") else value

    return {
        "movie": {
            "title": str(favorite["movie_title"]),
            "year": safe_value(favorite["year"]),
            "critic_rating": safe_value(favorite["critic_rating"]),
            "audience_rating": safe_value(favorite["audience_rating"]),
            "genres": str(favorite["genres"])
        },
        "genre": chosen_genre,
        "movie_count": int(len(genre_movies)),
        "statistics": stats,
        "histogram_interpretation": histogram_interpretation,
        "histogram_image": histogram_image,
        "correlation_interpretation": correlation_interpretation,
        "scatterplot_image": scatterplot_image
    }


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
            movie = str(payload.get("movie", "")).strip()
            genre = str(payload.get("genre", "")).strip()

            if not movie or not genre:
                self.send_json(400, {"error": "Enter both a movie title and a genre."})
                return

            result = analyze(movie, genre)
            self.send_json(200, result)
        except FileNotFoundError as exc:
            self.send_json(500, {"error": str(exc)})
        except ValueError as exc:
            self.send_json(400, {"error": str(exc)})
        except Exception:
            self.send_json(500, {"error": "An unexpected error occurred while analyzing the data."})

    def do_GET(self):
    request_path = urlparse(self.path)

    if request_path.path == "/api/movies":
        try:
            query = parse_qs(request_path.query).get("q", [""])[0].strip()

            if not query:
                self.send_json(200, {"movies": []})
                return

            if not DATA_PATH.exists():
                raise FileNotFoundError(
                    "rotten_tomatoes_movies.csv was not found."
                )

            movie_data = pd.read_csv(
                DATA_PATH,
                usecols=["movie_title"]
            )

            titles = (
                movie_data["movie_title"]
                .dropna()
                .astype(str)
                .drop_duplicates()
            )

            matches = titles[
                titles.str.contains(query, case=False, regex=False)
            ]

            # Show titles starting with the query before other matches.
            starts_with = matches[
                matches.str.casefold().str.startswith(query.casefold())
            ]
            other_matches = matches[
                ~matches.str.casefold().str.startswith(query.casefold())
            ]

            results = (
                starts_with.head(10).tolist()
                + other_matches.head(10).tolist()
            )[:10]

            self.send_json(200, {"movies": results})

        except FileNotFoundError as exc:
            self.send_json(500, {"error": str(exc)})
        except Exception:
            self.send_json(
                500,
                {"error": "Could not load movie suggestions."}
            )
    else:
        self.send_json(405, {"error": "Use POST to analyze a movie."})

    def send_json(self, status, payload):
        body = json.dumps(payload, allow_nan=False, default=str).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
