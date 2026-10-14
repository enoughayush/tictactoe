"""A content-based movie recommender with positive and negative feedback.

Run with:
    py recommendationsystem.py

Choose movies you like and dislike. The recommender compares their genres
and explains why each unseen movie was suggested. It uses only Python's
standard library and the small catalog below.
"""

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
    """Rank unseen movies using the user's liked and disliked genres."""
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


def parse_choices(answer: str) -> Set[int]:
    """Parse comma-separated movie numbers and validate each selection."""
    choices: Set[int] = set()
    for value in answer.split(","):
        value = value.strip()
        if not value:
            continue
        try:
            movie_id = int(value)
        except ValueError as exc:
            raise ValueError(f"'{value}' is not a number.") from exc
        if movie_id not in MOVIES:
            raise ValueError(f"Choose a number from 1 to {len(MOVIES)}.")
        choices.add(movie_id)
    return choices


def main() -> None:
    """Collect ratings and print ranked suggestions with matching genres."""
    print("MOVIE RECOMMENDATION SYSTEM")
    print("Rate a few movies; genre matches shape your recommendations.\n")
    for movie_id, (title, genres) in MOVIES.items():
        print(f"{movie_id:>2}. {title} ({', '.join(genres)})")

    try:
        liked_ids = parse_choices(input("\nMovies you like (numbers, e.g. 1, 4): "))
        disliked_ids = parse_choices(
            input("Movies you dislike (numbers, or press Enter to skip): ")
        )
    except (EOFError, KeyboardInterrupt):
        print("\nNo problem. Goodbye!")
        return
    except ValueError as exc:
        print(f"Input error: {exc}")
        return

    conflict = liked_ids & disliked_ids
    if conflict:
        print("A movie can't be both liked and disliked; keeping it as liked.")
        disliked_ids -= conflict

    suggestions = recommend(liked_ids, disliked_ids=disliked_ids)
    if not suggestions:
        print("No matching movies found. Try rating some titles you like.")
        return

    profile = build_profile(liked_ids, disliked_ids)
    print("\nRecommended for you:")
    for movie_id, score in suggestions:
        title, genres = MOVIES[movie_id]
        reasons = [genre for genre in genres if profile.get(genre, 0) > 0]
        print(f"- {title} — because you liked {', '.join(reasons)} (score {score:.2f})")


if __name__ == "__main__":
    main()
