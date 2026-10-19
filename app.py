import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

st.set_page_config(
    page_title="movie comparisons",
    page_icon="",
    layout="wide"
)

#Load Dataset
movieData = pd.read_csv('./rotten_tomatoes_movies.csv')

# Prepare columns
movieData["year"] = pd.to_numeric(movieData["year"], errors="coerce")
movieData["audience_rating"] = pd.to_numeric(
    movieData["audience_rating"], errors="coerce"
)
movieData["critic_rating"] = pd.to_numeric(
    movieData["critic_rating"], errors="coerce"
)

movieData = movieData.dropna(
    subset=["movie_title", "year", "genres",
            "audience_rating", "critic_rating"]
)

st.title("Movie Comparisons")
st.write(
    "This project uses the rotten tomatoes dataset to see how your favorite movie compares with others from the same genere!"
)

# Select fav
eligible = movieData[movieData["year"] < 2020]

if eligible.empty:
    st.error("No eligible movies were found in the dataset.")
    st.stop()

titles = sorted(eligible["movie_title"].unique())

favMovie = st.selectbox(
    "What is your favorite movie (released before 2020)?",
    titles
)

favData = eligible[eligible["movie_title"] == favMovie].iloc[0]

# Display movie information
st.subheader(f"Here is some info about {favMovie}")

c1, c2, c3 = st.columns(3)
c1.metric("Release Year", int(favData["year"]))
c2.metric("Critic Rating", f'{favData["critic_rating"]:.1f}%')
c3.metric("Audience Rating", f'{favData["audience_rating"]:.1f}%')

st.write("**Genres:**", favData["genres"])

# Select genre
genres = sorted({
    genre.strip()
    for genre in str(favData["genres"]).split(",")
    if genre.strip()
})

if not genres:
    st.warning("No genres are available for this movie.")
    st.stop()

chosenGenre = st.selectbox(
    "Which genre would you like to analyze?",
    genres
)

# Match as complete name
genreMovieData = eligible[
    eligible["genres"].apply(
        lambda value: chosenGenre in [
            genre.strip() for genre in str(value).split(",")
        ]
    )
].copy()

ratings = genreMovieData["audience_rating"]
favoriteRating = float(favData["audience_rating"])

st.divider()
st.header(f"How {favMovie} compares with {chosenGenre} movies")
st.write(f"**{len(genreMovieData)} movies** belong to this genre.")

# Summary statistics
minimum = ratings.min()
maximum = ratings.max()
mean = ratings.mean()
median = ratings.median()

a, b, c, d = st.columns(4)
a.metric("Lowest Rating", f"{minimum:.1f}%")
b.metric("Highest Rating", f"{maximum:.1f}%")
c.metric("Average Rating", f"{mean:.1f}%")
d.metric("Median Rating", f"{median:.1f}%")

st.subheader("Your movie vs. the genre")

st.write(
    f"Your movie is **{abs(favoriteRating - minimum):.1f} points** "
    "above the lowest audience rating."
)
st.write(
    f"Your movie is **{abs(maximum - favoriteRating):.1f} points** "
    "below the highest audience rating."
)

difference = favoriteRating - mean
if difference > 0:
    st.write(f"Your movie is {difference:.1f} points above the genre average.")
elif difference < 0:
    st.write(f"Your movie is {abs(difference):.1f} points below the genre average.")
else:
    st.write("Your movie matches the genre average.")

difference = favoriteRating - median
if difference > 0:
    st.write(f"Your movie is {difference:.1f} points above the genre median.")
elif difference < 0:
    st.write(f"Your movie is {abs(difference):.1f} points below the genre median.")
else:
    st.write("Your movie matches the genre median.")

# Visualizations
st.divider()
st.header("Explore the data")

left, right = st.columns(2)

with left:
    st.subheader("Audience Rating Distribution")

    fig1, ax1 = plt.subplots()
    counts, bins, _ = ax1.hist(
        ratings, bins=20, range=(0, 100), edgecolor="black"
    )
    ax1.set_title(f"Audience Ratings of {chosenGenre} Movies")
    ax1.set_xlabel("Audience Rating")
    ax1.set_ylabel("Number of Movies")
    ax1.grid(True, alpha=0.3)
    st.pyplot(fig1)
    plt.close(fig1)

    if len(counts) and counts.max() > 0:
        index = counts.argmax()
        st.write(
            f"Most movies fall in the rating range "
            f"{bins[index]:.0f}–{bins[index + 1]:.0f}."
        )

with right:
    st.subheader("Critic Ratings vs. Audience Ratings")

    fig2, ax2 = plt.subplots()
    ax2.scatter(
        genreMovieData["audience_rating"],
        genreMovieData["critic_rating"],
        alpha=0.5
    )
    ax2.set_title("Audience Rating vs. Critic Rating")
    ax2.set_xlabel("Audience Rating")
    ax2.set_ylabel("Critic Rating")
    ax2.set_xlim(0, 100)
    ax2.set_ylim(0, 100)
    ax2.grid(True, alpha=0.3)
    st.pyplot(fig2)
    plt.close(fig2)

    corr = ratings.corr(genreMovieData["critic_rating"])

    if pd.isna(corr):
        st.write("There isn't enough variation in the data to calculate correlation.")
    else:
        if corr > 0.3:
            relationship = "positive"
        elif corr < -0.3:
            relationship = "negative"
        else:
            relationship = "weak or little"

        st.write(
            f"The correlation is **{relationship}** "
            f"(correlation = {corr:.2f})."
        )

st.divider()
st.caption("Movie Comparisons | Data analysis with Python and pandas")
