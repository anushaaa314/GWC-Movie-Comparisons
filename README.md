# Movie Comparisons (Vercel)

This is a minimal web version of the original terminal-based movie analysis program.

## Files

- `index.html` — simple web form and results page
- `api/analyze.py` — Python API that runs the analysis and creates the two plots
- `rotten_tomatoes_movies.csv` — your original dataset (must be in the repository root)
- `requirements.txt` — Python dependencies
- `vercel.json` — includes the CSV in the deployed Python function

## Deploy

1. Copy these files into the root of your GitHub repository.
2. Make sure `rotten_tomatoes_movies.csv` is in the same root folder as `index.html`.
3. Commit and push the changes to GitHub.
4. In Vercel, import the GitHub repository and deploy it.
5. After deployment, enter a movie title exactly as it appears in the dataset, then enter a genre such as `Comedy` or `Drama`.

## Notes

- This keeps the original dataset-driven analysis and both visualizations.
- The movie title is matched without case sensitivity, but spelling should match the dataset.
- The genre search is case-insensitive and treats the genre as literal text.
- Test with a small sample locally before deploying if you change the dataset.
