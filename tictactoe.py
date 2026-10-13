import math

EMPTY = " "
WINNING_LINES = [
    (0, 1, 2),
    (3, 4, 5),
    (6, 7, 8),
    (0, 3, 6),
    (1, 4, 7),
    (2, 5, 8),
    (0, 4, 8),
    (2, 4, 6),
]


def print_board(board):
    cells = [cell if cell != EMPTY else str(index + 1) for index, cell in enumerate(board)]
    print(f"\n {cells[0]} | {cells[1]} | {cells[2]} ")
    print("---+---+---")
    print(f" {cells[3]} | {cells[4]} | {cells[5]} ")
    print("---+---+---")
    print(f" {cells[6]} | {cells[7]} | {cells[8]} \n")


def available_moves(board):
    return [index for index, spot in enumerate(board) if spot == EMPTY]


def is_full(board):
    return all(spot != EMPTY for spot in board)


def get_winner(board):
    for a, b, c in WINNING_LINES:
        if board[a] != EMPTY and board[a] == board[b] == board[c]:
            return board[a]
    return None


def get_best_move(board, ai_symbol, human_symbol):
    best_score = -math.inf
    best_move = None
    move_priority = [4, 0, 2, 6, 8, 1, 3, 5, 7]

    for move in available_moves(board):
        board[move] = ai_symbol
        score = minimax(board, 0, False, ai_symbol, human_symbol)
        board[move] = EMPTY

        if score > best_score:
            best_score = score
            best_move = move
        elif score == best_score:
            if move in move_priority and (best_move is None or move_priority.index(move) < move_priority.index(best_move)):
                best_move = move

    return best_move


def minimax(board, depth, is_ai_turn, ai_symbol, human_symbol):
    winner = get_winner(board)
    if winner == ai_symbol:
        return 10 - depth
    if winner == human_symbol:
        return depth - 10
    if is_full(board):
        return 0

    if is_ai_turn:
        best_score = -math.inf
        for move in available_moves(board):
            board[move] = ai_symbol
            score = minimax(board, depth + 1, False, ai_symbol, human_symbol)
            board[move] = EMPTY
            best_score = max(best_score, score)
        return best_score

    best_score = math.inf
    for move in available_moves(board):
        board[move] = human_symbol
        score = minimax(board, depth + 1, True, ai_symbol, human_symbol)
        board[move] = EMPTY
        best_score = min(best_score, score)
    return best_score


def safe_input(prompt):
    try:
        return input(prompt)
    except EOFError:
        print("\nInput stream closed. Exiting the game.")
        raise SystemExit(0)


def get_human_move(board):
    while True:
        try:
            move = int(safe_input("Choose a square (1-9): "))
        except ValueError:
            print("Please enter a number from 1 to 9.")
            continue

        if move < 1 or move > 9:
            print("Your move must be between 1 and 9.")
            continue

        index = move - 1
        if board[index] != EMPTY:
            print("That square is already taken. Try again.")
            continue

        return index


def prompt_for_symbol():
    while True:
        symbol = safe_input("Choose your symbol: X or O: ").strip().upper()
        if symbol in {"X", "O"}:
            return symbol
        print("Invalid choice. Please type X or O.")


def play_game():
    board = [EMPTY] * 9
    human_symbol = prompt_for_symbol()
    ai_symbol = "O" if human_symbol == "X" else "X"
    current_player = "human" if human_symbol == "X" else "ai"

    print("\nAI opponent is ready. You are playing as", human_symbol)
    print("Board positions are numbered 1 through 9.")

    while True:
        if current_player == "human":
            print_board(board)
            move = get_human_move(board)
            board[move] = human_symbol
            current_player = "ai"
        else:
            print("AI is thinking...")
            move = get_best_move(board, ai_symbol, human_symbol)
            board[move] = ai_symbol
            print(f"AI plays at square {move + 1}.")
            current_player = "human"

        winner = get_winner(board)
        if winner:
            print_board(board)
            if winner == human_symbol:
                print("You win! Great job.")
            else:
                print("AI wins! Better luck next time.")
            break

        if is_full(board):
            print_board(board)
            print("It's a draw!")
            break


def main():
    print("Welcome to Tic-Tac-Toe against an AI opponent!")

    while True:
        play_game()
        again = input("Play again? (y/n): ").strip().lower()
        if again not in {"y", "yes"}:
            print("Thanks for playing!")
            break


if __name__ == "__main__":
    main()
