"""A simple movie recommendation system using genre matching.

Run with:
    py recommendationsystem.py

Type one or more movie titles from the catalog, separated by commas.
"""

import tkinter as tk
from tkinter import messagebox

# The recommender can suggest only movies in this small built-in catalog.
MOVIES = {
    "The Matrix": ["action", "science fiction"],
    "Inception": ["action", "science fiction", "thriller"],
    "Interstellar": ["adventure", "science fiction", "drama"],
    "The Dark Knight": ["action", "crime", "drama"],
    "Spider-Man: Into the Spider-Verse": ["action", "adventure", "animation"],
    "Toy Story": ["animation", "adventure", "comedy"],
    "Finding Nemo": ["animation", "adventure", "comedy"],
    "The Grand Budapest Hotel": ["comedy", "adventure"],
    "Parasite": ["thriller", "drama", "comedy"],
    "Knives Out": ["mystery", "comedy", "crime"],
    "Get Out": ["horror", "mystery", "thriller"],
    "A Quiet Place": ["horror", "thriller", "drama"],
    "Pride & Prejudice": ["romance", "drama"],
    "La La Land": ["romance", "drama", "music"],
    "The Shawshank Redemption": ["drama", "crime"],
    "Mad Max: Fury Road": ["action", "adventure", "science fiction"],
    "Coco": ["animation", "adventure", "music", "drama"],
    "The Princess Bride": ["adventure", "comedy", "romance"],
}


def recommend_movies(liked_movies, number_of_recommendations=5):
    """Return catalog movies that share genres with the user's titles."""
    genre_preferences = {}

    for movie in liked_movies:
        for genre in MOVIES[movie]:
            genre_preferences[genre] = genre_preferences.get(genre, 0) + 1

    scores = {}
    for movie, genres in MOVIES.items():
        if movie in liked_movies:
            continue

        score = sum(genre_preferences.get(genre, 0) for genre in genres)
        if score > 0:
            scores[movie] = score

    ranked_movies = sorted(scores, key=scores.get, reverse=True)
    return ranked_movies[:number_of_recommendations]


def show_recommendations():
    """Check the typed titles and show matching movie recommendations."""
    typed_titles = [title.strip() for title in title_entry.get().split(",") if title.strip()]
    if not typed_titles:
        messagebox.showinfo("Enter a movie", "Type at least one movie title first.")
        return

    # Match without case sensitivity but use the catalog's official spelling.
    catalog_titles = {title.lower(): title for title in MOVIES}
    liked_movies = []
    unknown_titles = []
    for title in typed_titles:
        catalog_title = catalog_titles.get(title.lower())
        if catalog_title is None:
            unknown_titles.append(title)
        elif catalog_title not in liked_movies:
            liked_movies.append(catalog_title)

    if unknown_titles:
        messagebox.showerror(
            "Movie not in catalog",
            "I couldn't find: " + ", ".join(unknown_titles)
            + "\nUse a title shown in the catalog list.",
        )
        return

    suggestions = recommend_movies(liked_movies)
    recommendation_list.delete(0, tk.END)
    if not suggestions:
        recommendation_list.insert(tk.END, "No similar movies found.")
        return

    for movie in suggestions:
        genres = ", ".join(MOVIES[movie])
        recommendation_list.insert(tk.END, f"{movie} ({genres})")


# Create a basic window for entering preferences and viewing suggestions.
window = tk.Tk()
window.title("Movie Recommendation System")
window.geometry("650x720")

heading = tk.Label(window, text="Movie Recommendation System", font=("Arial", 18, "bold"))
heading.pack(pady=(16, 6))

instructions = tk.Label(
    window,
    text="Type the movies you like, separated by commas. Recommendations use shared genres.",
    wraplength=580,
)
instructions.pack(pady=(0, 10))

title_entry = tk.Entry(window, width=68)
title_entry.pack(padx=20, pady=(0, 8), fill="x")
tk.Label(window, text="Example: The Matrix, Inception", fg="gray").pack(anchor="w", padx=22, pady=(0, 6))

catalog_heading = tk.Label(window, text="Titles you can enter:", font=("Arial", 11, "bold"))
catalog_heading.pack(anchor="w", padx=25, pady=(8, 3))

catalog_frame = tk.Frame(window)
catalog_frame.pack(padx=20, pady=4, fill="x")
catalog_scrollbar = tk.Scrollbar(catalog_frame)
catalog_scrollbar.pack(side="right", fill="y")
catalog_list = tk.Listbox(
    catalog_frame, height=13, width=60, yscrollcommand=catalog_scrollbar.set
)
catalog_list.pack(side="left", fill="both", expand=True)
catalog_scrollbar.configure(command=catalog_list.yview)
for movie_title in MOVIES:
    catalog_list.insert(tk.END, movie_title)
catalog_list.configure(state=tk.DISABLED)

recommend_button = tk.Button(
    window, text="Get Recommendations", command=show_recommendations, padx=12, pady=6
)
recommend_button.pack(pady=10)

results_heading = tk.Label(window, text="Recommended movies:", font=("Arial", 12, "bold"))
results_heading.pack(anchor="w", padx=25)

recommendation_list = tk.Listbox(window, height=7, width=60)
recommendation_list.pack(padx=20, pady=(5, 15), fill="both", expand=True)

window.mainloop()

