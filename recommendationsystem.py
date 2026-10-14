"""A simple movie recommendation system using genre matching.

Run with:
    py recommendationsystem.py

Select movies you like, then click the button to see similar movies.
"""

import tkinter as tk
from tkinter import messagebox

# Movie titles are matched to a short list of genres.
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
    """Return movies with the most genres in common with the selected movies."""
    genre_preferences = {}

    for movie in liked_movies:
        for genre in MOVIES[movie]:
            genre_preferences[genre] = genre_preferences.get(genre, 0) + 1

    scores = {}
    for movie, genres in MOVIES.items():
        if movie in liked_movies:
            continue

        score = 0
        for genre in genres:
            score += genre_preferences.get(genre, 0)
        if score > 0:
            scores[movie] = score

    ranked_movies = sorted(scores, key=scores.get, reverse=True)
    return ranked_movies[:number_of_recommendations]


def show_recommendations():
    """Read the selected movies and display recommendations in the window."""
    selected_indexes = movie_list.curselection()
    if not selected_indexes:
        messagebox.showinfo("Choose movies", "Select at least one movie you like.")
        return

    liked_movies = [movie_list.get(index) for index in selected_indexes]
    suggestions = recommend_movies(liked_movies)

    recommendation_list.delete(0, tk.END)
    if not suggestions:
        recommendation_list.insert(tk.END, "No similar movies found.")
        return

    for movie in suggestions:
        genres = ", ".join(MOVIES[movie])
        recommendation_list.insert(tk.END, f"{movie} ({genres})")


# Create a small, simple desktop window.
window = tk.Tk()
window.title("Movie Recommendation System")
window.geometry("600x620")

heading = tk.Label(window, text="Movie Recommendation System", font=("Arial", 18, "bold"))
heading.pack(pady=(18, 6))

instructions = tk.Label(
    window,
    text="Select movies you like. The program will suggest movies with similar genres.",
    wraplength=520,
)
instructions.pack(pady=(0, 12))

movie_list = tk.Listbox(window, selectmode=tk.MULTIPLE, height=14, width=55, exportselection=False)
movie_list.pack(padx=20, pady=5, fill="x")
for movie_title in MOVIES:
    movie_list.insert(tk.END, movie_title)

recommend_button = tk.Button(
    window, text="Get Recommendations", command=show_recommendations, padx=12, pady=6
)
recommend_button.pack(pady=12)

results_heading = tk.Label(window, text="Recommended movies:", font=("Arial", 12, "bold"))
results_heading.pack(anchor="w", padx=25)

recommendation_list = tk.Listbox(window, height=7, width=55)
recommendation_list.pack(padx=20, pady=(5, 16), fill="both", expand=True)

window.mainloop()
