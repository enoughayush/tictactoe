"""AI-Based Tic-Tac-Toe Game with a minimax computer opponent."""

import random
from math import inf
from typing import List, Optional, Tuple

Board = List[str]
EMPTY = " "
WINNING_LINES: Tuple[Tuple[int, int, int], ...] = (
    (0, 1, 2),
    (3, 4, 5),
    (6, 7, 8),
    (0, 3, 6),
    (1, 4, 7),
    (2, 5, 8),
    (0, 4, 8),
    (2, 4, 6),
)
MOVE_PRIORITY = (4, 0, 2, 6, 8, 1, 3, 5, 7)


def print_board(board: Board) -> None:
    """Display the board, numbering each empty square for the next move."""
    cells = [cell if cell != EMPTY else str(index + 1) for index, cell in enumerate(board)]
    print(f"\n  {cells[0]} | {cells[1]} | {cells[2]} ")
    print(" ---+---+---")
    print(f"  {cells[3]} | {cells[4]} | {cells[5]} ")
    print(" ---+---+---")
    print(f"  {cells[6]} | {cells[7]} | {cells[8]} \n")


def available_moves(board: Board) -> List[int]:
    """Return the indexes of all unoccupied squares."""
    return [index for index, spot in enumerate(board) if spot == EMPTY]


def is_full(board: Board) -> bool:
    """Return True when no empty squares remain."""
    return all(spot != EMPTY for spot in board)


def get_winner(board: Board) -> Optional[str]:
    """Return the winning symbol, or None if the game has no winner yet."""
    for first, second, third in WINNING_LINES:
        if board[first] != EMPTY and board[first] == board[second] == board[third]:
            return board[first]
    return None


def get_best_move(board: Board, ai_symbol: str, human_symbol: str) -> Optional[int]:
    """Choose the AI's strongest available move with deterministic tie-breaking."""
    best_score = -inf
    best_move = None

    for move in sorted(available_moves(board), key=MOVE_PRIORITY.index):
        board[move] = ai_symbol
        score = minimax(board, 0, False, ai_symbol, human_symbol)
        board[move] = EMPTY

        if score > best_score:
            best_score = score
            best_move = move

    return best_move


def minimax(
    board: Board,
    depth: int,
    is_ai_turn: bool,
    ai_symbol: str,
    human_symbol: str,
) -> float:
    """Score a board position assuming both players choose optimally."""
    winner = get_winner(board)
    if winner == ai_symbol:
        return 10 - depth
    if winner == human_symbol:
        return depth - 10
    if is_full(board):
        return 0

    if is_ai_turn:
        best_score = -inf
        for move in available_moves(board):
            board[move] = ai_symbol
            score = minimax(board, depth + 1, False, ai_symbol, human_symbol)
            board[move] = EMPTY
            best_score = max(best_score, score)
        return best_score

    best_score = inf
    for move in available_moves(board):
        board[move] = human_symbol
        score = minimax(board, depth + 1, True, ai_symbol, human_symbol)
        board[move] = EMPTY
        best_score = min(best_score, score)
    return best_score


def get_ai_move(board: Board, ai_symbol: str, human_symbol: str, difficulty: str) -> Optional[int]:
    """Choose a move at the selected strength: easy, medium, or hard."""
    moves = available_moves(board)
    if not moves:
        return None
    if difficulty == "easy":
        return random.choice(moves)
    if difficulty == "medium":
        # Take a winning move first, then block an immediate human win.
        for symbol in (ai_symbol, human_symbol):
            for move in moves:
                board[move] = symbol
                wins = get_winner(board) == symbol
                board[move] = EMPTY
                if wins:
                    return move
        return random.choice(moves)
    return get_best_move(board, ai_symbol, human_symbol)

def safe_input(prompt: str) -> str:
    """Read terminal input and exit cleanly if the input stream closes."""
    try:
        return input(prompt)
    except EOFError:
        print("\nInput stream closed. Exiting the game.")
        raise SystemExit(0)


def get_human_move(board: Board) -> int:
    """Prompt until the player chooses an available square from 1 to 9."""
    while True:
        try:
            move = int(safe_input("Choose a square (1-9): "))
        except ValueError:
            print("Please enter a number from 1 to 9.")
            continue

        if not 1 <= move <= 9:
            print("Your move must be between 1 and 9.")
            continue

        index = move - 1
        if board[index] != EMPTY:
            print("That square is already taken. Choose another one.")
            continue
        return index


def prompt_for_symbol() -> str:
    """Ask the player whether they want to play as X or O."""
    while True:
        symbol = safe_input("Choose your symbol (X/O): ").strip().upper()
        if symbol in {"X", "O"}:
            return symbol
        print("Please enter X or O.")


def prompt_for_difficulty() -> str:
    """Ask the player to choose how challenging the computer should be."""
    while True:
        choice = safe_input("Choose difficulty (easy/medium/hard): ").strip().lower()
        if choice in {"easy", "medium", "hard"}:
            return choice
        print("Please enter easy, medium, or hard.")

def play_game() -> None:
    """Play one complete game against the computer opponent."""
    board = [EMPTY] * 9
    human_symbol = prompt_for_symbol()
    difficulty = prompt_for_difficulty()
    ai_symbol = "O" if human_symbol == "X" else "X"
    current_player = "human" if human_symbol == "X" else "ai"

    print(f"\nYou are {human_symbol}; the computer is {ai_symbol} ({difficulty} mode).")
    print("Choose a square by entering its number.")

    while True:
        if current_player == "human":
            print_board(board)
            board[get_human_move(board)] = human_symbol
            current_player = "ai"
        else:
            print("\nComputer is thinking...")
            move = get_ai_move(board, ai_symbol, human_symbol, difficulty)
            if move is None:
                break
            board[move] = ai_symbol
            print(f"Computer chose square {move + 1}.")
            current_player = "human"

        winner = get_winner(board)
        if winner:
            print_board(board)
            if winner == human_symbol:
                print("You win! Great game.")
            else:
                print("The computer wins. Better luck next time!")
            return

        if is_full(board):
            print_board(board)
            print("It's a draw!")
            return


def main() -> None:
    """Display the game menu and offer another round after each game."""
    print("=" * 52)
    print("             AI-BASED TIC-TAC-TOE GAME")
    print("=" * 52)
    print("Get three of your symbols in a row to win.\n")

    while True:
        play_game()
        again = safe_input("Play another round? (y/n): ").strip().lower()
        if again not in {"y", "yes"}:
            print("Thanks for playing. See you next time!")
            break


if __name__ == "__main__":
    main()



