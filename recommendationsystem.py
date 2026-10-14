"""CineMatch: a small desktop movie recommender.

Run with:
    py recommendationsystem.py

Rate movies with Like or Not for me. CineMatch uses their genres to rank
unrated titles and explain each recommendation. The interface uses Tkinter,
which is included with most Windows Python installations.
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, List, Optional, Set, Tuple

Movie = Tuple[str, Tuple[str, ...]]
MOVIES: Dict[int, Movie] = {
    1: ("The Matrix", ("action", "science fiction")),
    2: ("Inception", ("action", "science fiction", "thriller")),
    3: ("Interstellar", ("adventure", "science fiction", "drama")),
    4: ("The Dark Knight", ("action", "crime", "drama")),
    5: ("Spider-Man: Into the Spider-Verse", ("action", "adventure", "animation")),
    6: ("Toy Story", ("animation", "adventure", "comedy")),
    7: ("Finding Nemo", ("animation", "adventure", "comedy")),
    8: ("The Grand Budapest Hotel", ("comedy", "adventure")),
    9: ("Parasite", ("thriller", "drama", "comedy")),
    10: ("Knives Out", ("mystery", "comedy", "crime")),
    11: ("Get Out", ("horror", "mystery", "thriller")),
    12: ("A Quiet Place", ("horror", "thriller", "drama")),
    13: ("Pride & Prejudice", ("romance", "drama")),
    14: ("La La Land", ("romance", "drama", "music")),
    15: ("The Shawshank Redemption", ("drama", "crime")),
    16: ("Mad Max: Fury Road", ("action", "adventure", "science fiction")),
    17: ("Coco", ("animation", "adventure", "music", "drama")),
    18: ("The Princess Bride", ("adventure", "comedy", "romance")),
}

COLORS = {
    "background": "#0B1020",
    "panel": "#121A2B",
    "card": "#19243A",
    "card_hover": "#202E48",
    "text": "#F2F5FC",
    "muted": "#97A6C0",
    "accent": "#78E0C1",
    "accent_dark": "#163A39",
    "pink": "#FF8FA3",
    "pink_dark": "#442533",
    "border": "#263550",
    "button": "#263550",
}


def build_profile(liked_ids: Set[int], disliked_ids: Set[int]) -> Dict[str, float]:
    """Build genre preferences, subtracting genres from disliked titles."""
    profile: Dict[str, float] = {}
    for movie_id in liked_ids:
        for genre in MOVIES[movie_id][1]:
            profile[genre] = profile.get(genre, 0.0) + 1.0
    for movie_id in disliked_ids:
        for genre in MOVIES[movie_id][1]:
            profile[genre] = profile.get(genre, 0.0) - 1.0
    return profile


def recommend(
    liked_ids: Set[int], limit: int = 5, disliked_ids: Optional[Set[int]] = None
) -> List[Tuple[int, float]]:
    """Rank unrated movies by their average match with the user's genre profile."""
    if limit <= 0:
        return []
    liked_ids = {movie_id for movie_id in liked_ids if movie_id in MOVIES}
    disliked_ids = {
        movie_id for movie_id in (disliked_ids or set()) if movie_id in MOVIES
    } - liked_ids
    if not liked_ids:
        return []

    profile = build_profile(liked_ids, disliked_ids)
    rated_ids = liked_ids | disliked_ids
    ranked: List[Tuple[int, float]] = []
    for movie_id, (_, genres) in MOVIES.items():
        if movie_id in rated_ids:
            continue
        score = sum(profile.get(genre, 0.0) for genre in genres) / len(genres)
        if score > 0:
            ranked.append((movie_id, score))

    ranked.sort(key=lambda item: (-item[1], MOVIES[item[0]][0]))
    return ranked[:limit]


class MovieRecommenderApp:
    """Dark themed desktop interface for rating movies and seeing suggestions."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("CineMatch — Movie Recommendations")
        self.root.geometry("1120x820")
        self.root.minsize(900, 650)
        self.root.configure(bg=COLORS["background"])
        style = ttk.Style(self.root)
        style.theme_use("clam")
        style.configure(
            "TCombobox",
            fieldbackground=COLORS["card"], background=COLORS["card"],
            foreground=COLORS["text"], arrowcolor=COLORS["accent"],
            bordercolor=COLORS["border"], padding=7,
        )
        style.map(
            "TCombobox",
            fieldbackground=[("readonly", COLORS["card"])],
            foreground=[("readonly", COLORS["text"])],
            selectbackground=[("readonly", COLORS["card"])],
            selectforeground=[("readonly", COLORS["text"])],
        )
        self.ratings: Dict[int, int] = {}
        self.search_var = tk.StringVar()
        self.genre_var = tk.StringVar(value="All genres")
        self.card_widgets: Dict[int, Tuple[tk.Button, tk.Button]] = {}
        self.recommendation_frame: Optional[tk.Frame] = None

        self._build_layout()
        self.search_var.trace_add("write", lambda *_: self._render_movies())
        self.genre_var.trace_add("write", lambda *_: self._render_movies())
        self._render_movies()
        self._render_recommendations()

    def _label(self, parent: tk.Widget, text: str, **kwargs) -> tk.Label:
        options = {
            "text": text,
            "bg": COLORS["panel"],
            "fg": COLORS["text"],
            "font": ("Segoe UI", 10),
            "anchor": "w",
        }
        options.update(kwargs)
        return tk.Label(parent, **options)

    def _build_layout(self) -> None:
        outer = tk.Frame(self.root, bg=COLORS["background"], padx=28, pady=22)
        outer.pack(fill="both", expand=True)

        brand_row = tk.Frame(outer, bg=COLORS["background"])
        brand_row.pack(fill="x", pady=(0, 18))
        tk.Label(
            brand_row,
            text="CINEMATCH",
            bg=COLORS["background"],
            fg=COLORS["accent"],
            font=("Segoe UI", 11, "bold"),
        ).pack(side="left")
        tk.Label(
            brand_row,
            text="PERSONAL MOVIE PICKS",
            bg=COLORS["background"],
            fg=COLORS["muted"],
            font=("Segoe UI", 9, "bold"),
        ).pack(side="right")

        tk.Label(
            outer,
            text="Find your next favorite.",
            bg=COLORS["background"],
            fg=COLORS["text"],
            font=("Segoe UI", 28, "bold"),
            anchor="w",
        ).pack(fill="x")
        tk.Label(
            outer,
            text="Rate a few movies. We’ll use their genres to find something you’ll enjoy.",
            bg=COLORS["background"],
            fg=COLORS["muted"],
            font=("Segoe UI", 11),
            anchor="w",
        ).pack(fill="x", pady=(5, 20))

        content = tk.Frame(outer, bg=COLORS["background"])
        content.pack(fill="both", expand=True)
        content.grid_columnconfigure(0, weight=3, uniform="columns")
        content.grid_columnconfigure(1, weight=2, uniform="columns")
        content.grid_rowconfigure(0, weight=1)

        self.catalog_panel = tk.Frame(
            content, bg=COLORS["panel"], padx=18, pady=16,
            highlightthickness=1, highlightbackground=COLORS["border"],
        )
        self.catalog_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        self.recommendation_panel = tk.Frame(
            content, bg=COLORS["panel"], padx=20, pady=18,
            highlightthickness=1, highlightbackground=COLORS["border"],
        )
        self.recommendation_panel.grid(row=0, column=1, sticky="nsew", padx=(12, 0))

        self._build_catalog()
        self._build_recommendation_panel()

    def _build_catalog(self) -> None:
        heading = tk.Frame(self.catalog_panel, bg=COLORS["panel"])
        heading.pack(fill="x")
        tk.Label(
            heading, text="Explore movies", bg=COLORS["panel"], fg=COLORS["text"],
            font=("Segoe UI", 16, "bold"),
        ).pack(side="left")
        self.rating_count_label = tk.Label(
            heading, text="0 rated", bg=COLORS["panel"], fg=COLORS["muted"],
            font=("Segoe UI", 9),
        )
        self.rating_count_label.pack(side="right", pady=(5, 0))

        controls = tk.Frame(self.catalog_panel, bg=COLORS["panel"])
        controls.pack(fill="x", pady=(14, 12))
        self.search_entry = tk.Entry(
            controls, textvariable=self.search_var, bg=COLORS["card"],
            fg=COLORS["text"], insertbackground=COLORS["text"],
            relief="flat", font=("Segoe UI", 10),
        )
        self.search_entry.pack(side="left", fill="x", expand=True, ipady=9, padx=(0, 9))
        self.search_entry.insert(0, "Search titles or genres...")
        self.search_entry.configure(fg=COLORS["muted"])
        self.search_entry.bind("<FocusIn>", self._clear_search_placeholder)
        self.search_entry.bind("<FocusOut>", self._restore_search_placeholder)
        self.genre_box = ttk.Combobox(
            controls, textvariable=self.genre_var,
            values=["All genres"] + sorted({genre for _, genres in MOVIES.values() for genre in genres}),
            state="readonly", width=17,
        )
        self.genre_box.pack(side="right", ipady=4)

        self.canvas = tk.Canvas(
            self.catalog_panel, bg=COLORS["panel"], highlightthickness=0,
        )
        scrollbar = tk.Scrollbar(
            self.catalog_panel, orient="vertical", command=self.canvas.yview,
            bg=COLORS["panel"], troughcolor=COLORS["background"],
            activebackground=COLORS["accent"], relief="flat",
        )
        self.canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.movie_grid = tk.Frame(self.canvas, bg=COLORS["panel"])
        self.canvas_window = self.canvas.create_window(
            (0, 0), window=self.movie_grid, anchor="nw"
        )
        self.movie_grid.bind(
            "<Configure>",
            lambda _event: self.canvas.configure(scrollregion=self.canvas.bbox("all")),
        )
        self.canvas.bind(
            "<Configure>",
            lambda event: self.canvas.itemconfigure(self.canvas_window, width=event.width),
        )
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _build_recommendation_panel(self) -> None:
        tk.Label(
            self.recommendation_panel, text="Your picks", bg=COLORS["panel"],
            fg=COLORS["text"], font=("Segoe UI", 17, "bold"), anchor="w",
        ).pack(fill="x")
        tk.Label(
            self.recommendation_panel,
            text="Suggestions update as you rate movies.",
            bg=COLORS["panel"], fg=COLORS["muted"],
            font=("Segoe UI", 9), anchor="w",
        ).pack(fill="x", pady=(4, 12))

        summary = tk.Frame(self.recommendation_panel, bg=COLORS["panel"])
        summary.pack(fill="x", pady=(0, 15))
        self.like_summary = tk.Label(
            summary, text="♥  0 liked", bg=COLORS["accent_dark"],
            fg=COLORS["accent"], font=("Segoe UI", 9, "bold"), padx=10, pady=6,
        )
        self.like_summary.pack(side="left", padx=(0, 7))
        self.dislike_summary = tk.Label(
            summary, text="×  0 not for me", bg=COLORS["pink_dark"],
            fg=COLORS["pink"], font=("Segoe UI", 9, "bold"), padx=10, pady=6,
        )
        self.dislike_summary.pack(side="left")
        clear = tk.Button(
            summary, text="Clear", command=self._clear_ratings,
            bg=COLORS["panel"], fg=COLORS["muted"], activebackground=COLORS["card"],
            activeforeground=COLORS["text"], relief="flat", cursor="hand2",
            font=("Segoe UI", 9), padx=8,
        )
        clear.pack(side="right")

        self.result_area = tk.Frame(self.recommendation_panel, bg=COLORS["panel"])
        self.result_area.pack(fill="both", expand=True)
        self._render_recommendations()

        footer = tk.Label(
            self.recommendation_panel,
            text="Recommendations are based on genre similarity.",
            bg=COLORS["panel"], fg=COLORS["muted"],
            font=("Segoe UI", 8), anchor="w", wraplength=340,
        )
        footer.pack(fill="x", pady=(10, 0))

    def _clear_search_placeholder(self, _event=None) -> None:
        if self.search_entry.get() == "Search titles or genres...":
            self.search_entry.delete(0, "end")
            self.search_entry.configure(fg=COLORS["text"])

    def _restore_search_placeholder(self, _event=None) -> None:
        if not self.search_entry.get().strip():
            self.search_entry.insert(0, "Search titles or genres...")
            self.search_entry.configure(fg=COLORS["muted"])

    def _on_mousewheel(self, event) -> None:
        widget = self.root.winfo_containing(event.x_root, event.y_root)
        if widget is None:
            return
        current = widget
        while current is not None:
            if current == self.canvas or current == self.movie_grid:
                self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
                return
            current = getattr(current, "master", None)

    def _filtered_movies(self) -> List[int]:
        query = self.search_var.get().strip().lower()
        if query == "search titles or genres...":
            query = ""
        genre = self.genre_var.get()
        return [
            movie_id for movie_id, (title, genres) in MOVIES.items()
            if (not query or query in title.lower() or any(query in item for item in genres))
            and (genre == "All genres" or genre in genres)
        ]

    def _render_movies(self) -> None:
        for child in self.movie_grid.winfo_children():
            child.destroy()
        self.card_widgets.clear()
        self.movie_grid.grid_columnconfigure(0, weight=1, uniform="movie")
        self.movie_grid.grid_columnconfigure(1, weight=1, uniform="movie")

        for index, movie_id in enumerate(self._filtered_movies()):
            title, genres = MOVIES[movie_id]
            row, column = divmod(index, 2)
            card = tk.Frame(
                self.movie_grid, bg=COLORS["card"], padx=12, pady=11,
                highlightthickness=1, highlightbackground=COLORS["border"],
            )
            card.grid(row=row, column=column, sticky="nsew", padx=5, pady=5)
            card.grid_columnconfigure(0, weight=1)
            tk.Label(
                card, text=title, bg=COLORS["card"], fg=COLORS["text"],
                font=("Segoe UI", 10, "bold"), anchor="w", justify="left",
                wraplength=250,
            ).grid(row=0, column=0, columnspan=2, sticky="ew")
            tk.Label(
                card, text="  ·  ".join(genres), bg=COLORS["card"],
                fg=COLORS["muted"], font=("Segoe UI", 8), anchor="w",
                wraplength=250,
            ).grid(row=1, column=0, columnspan=2, sticky="ew", pady=(4, 10))

            liked = self.ratings.get(movie_id) == 1
            disliked = self.ratings.get(movie_id) == -1
            like_button = tk.Button(
                card, text="♥  Like", command=lambda mid=movie_id: self._rate(mid, 1),
                bg=COLORS["accent_dark"] if liked else COLORS["button"],
                fg=COLORS["accent"] if liked else COLORS["text"],
                activebackground=COLORS["accent_dark"], activeforeground=COLORS["accent"],
                relief="flat", cursor="hand2", font=("Segoe UI", 8, "bold"), pady=5,
            )
            like_button.grid(row=2, column=0, sticky="ew", padx=(0, 4))
            dislike_button = tk.Button(
                card, text="×  Not for me", command=lambda mid=movie_id: self._rate(mid, -1),
                bg=COLORS["pink_dark"] if disliked else COLORS["button"],
                fg=COLORS["pink"] if disliked else COLORS["text"],
                activebackground=COLORS["pink_dark"], activeforeground=COLORS["pink"],
                relief="flat", cursor="hand2", font=("Segoe UI", 8, "bold"), pady=5,
            )
            dislike_button.grid(row=2, column=1, sticky="ew", padx=(4, 0))
            self.card_widgets[movie_id] = (like_button, dislike_button)

        if not self._filtered_movies():
            tk.Label(
                self.movie_grid, text="No movies match that search.",
                bg=COLORS["panel"], fg=COLORS["muted"],
                font=("Segoe UI", 10), pady=25,
            ).grid(row=0, column=0, columnspan=2)
        self._update_counts()

    def _update_counts(self) -> None:
        liked = sum(rating == 1 for rating in self.ratings.values())
        disliked = sum(rating == -1 for rating in self.ratings.values())
        self.rating_count_label.configure(text=f"{liked + disliked} rated")
        self.like_summary.configure(text=f"♥  {liked} liked")
        self.dislike_summary.configure(text=f"×  {disliked} not for me")

    def _rate(self, movie_id: int, rating: int) -> None:
        if self.ratings.get(movie_id) == rating:
            self.ratings.pop(movie_id, None)
        else:
            self.ratings[movie_id] = rating
        self._render_movies()
        self._render_recommendations()

    def _clear_ratings(self) -> None:
        self.ratings.clear()
        self._render_movies()
        self._render_recommendations()

    def _render_recommendations(self) -> None:
        if self.recommendation_frame is not None:
            self.recommendation_frame.destroy()
        self.recommendation_frame = tk.Frame(self.result_area, bg=COLORS["panel"])
        self.recommendation_frame.pack(fill="both", expand=True)

        liked_ids = {movie_id for movie_id, rating in self.ratings.items() if rating == 1}
        disliked_ids = {movie_id for movie_id, rating in self.ratings.items() if rating == -1}
        if not liked_ids:
            tk.Label(
                self.recommendation_frame,
                text="Start with a like",
                bg=COLORS["panel"], fg=COLORS["text"],
                font=("Segoe UI", 14, "bold"), anchor="w",
            ).pack(fill="x", pady=(12, 3))
            tk.Label(
                self.recommendation_frame,
                text="Tap Like on movies you enjoy. We’ll find unrated titles with similar genres.",
                bg=COLORS["panel"], fg=COLORS["muted"],
                font=("Segoe UI", 10), justify="left", anchor="nw",
                wraplength=330,
            ).pack(fill="x")
            return

        suggestions = recommend(liked_ids, limit=6, disliked_ids=disliked_ids)
        profile = build_profile(liked_ids, disliked_ids)
        if not suggestions:
            tk.Label(
                self.recommendation_frame,
                text="No close matches yet. Try liking another movie.",
                bg=COLORS["panel"], fg=COLORS["muted"],
                font=("Segoe UI", 10), wraplength=330, justify="left",
            ).pack(fill="x", pady=12)
            return

        for rank, (movie_id, score) in enumerate(suggestions, start=1):
            title, genres = MOVIES[movie_id]
            reasons = [genre for genre in genres if profile.get(genre, 0) > 0]
            self._recommendation_card(rank, title, genres, reasons, score)

    def _recommendation_card(
        self, rank: int, title: str, genres: Tuple[str, ...],
        reasons: List[str], score: float,
    ) -> None:
        card = tk.Frame(
            self.recommendation_frame, bg=COLORS["card"], padx=13, pady=12,
            highlightthickness=1, highlightbackground=COLORS["border"],
        )
        card.pack(fill="x", pady=5)
        top = tk.Frame(card, bg=COLORS["card"])
        top.pack(fill="x")
        tk.Label(
            top, text=f"{rank:02d}", bg=COLORS["accent_dark"], fg=COLORS["accent"],
            font=("Segoe UI", 9, "bold"), padx=7, pady=3,
        ).pack(side="left", padx=(0, 8))
        tk.Label(
            top, text=title, bg=COLORS["card"], fg=COLORS["text"],
            font=("Segoe UI", 10, "bold"), anchor="w", justify="left",
            wraplength=270,
        ).pack(side="left", fill="x", expand=True)
        tk.Label(
            card, text="  ·  ".join(genres), bg=COLORS["card"],
            fg=COLORS["muted"], font=("Segoe UI", 8), anchor="w",
            wraplength=300,
        ).pack(fill="x", pady=(7, 4))
        reason_text = "Matches your interest in " + ", ".join(reasons)
        tk.Label(
            card, text=reason_text, bg=COLORS["card"], fg=COLORS["accent"],
            font=("Segoe UI", 8), anchor="w", wraplength=300,
        ).pack(fill="x")


def main() -> None:
    """Launch CineMatch's desktop interface."""
    root = tk.Tk()
    MovieRecommenderApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()


