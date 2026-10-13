# Python Console Projects

A small collection of interactive Python programs that run in the terminal. The repository currently contains a rule-based chatbot and a Tic-Tac-Toe game against a computer opponent.

## Projects

### Rule-Based Chatbot — `chatbot.py`

An offline chatbot that responds to a set of predefined topics and commands.

- Handles greetings, simple conversation, jokes, study topics, and a few programming questions.
- Answers basic arithmetic expressions such as `12 * (3 + 2)`.
- Shares the capitals of France, India, Japan, Italy, and Canada.
- Displays the computer's current date and time.
- Explains when a question is outside its predefined rules.

The chatbot works offline. It does not use a language model or access live information such as weather.

### Tic-Tac-Toe — `tictactoe.py`

A two-symbol, single-player game against a computer opponent.

- Choose to play as **X** or **O**.
- Select a square by entering its number from 1 to 9.
- The computer uses the minimax algorithm to choose its moves.
- Play another round when a game ends.

## Requirements

- Python 3.8 or later
- No third-party packages required

## Run the programs

Open a terminal in the project folder and start either program:

```powershell
py chatbot.py
```

```powershell
py tictactoe.py
```

If your system uses `python` instead of the Windows `py` launcher, run `python chatbot.py` or `python tictactoe.py`.

## Playing Tic-Tac-Toe

The game numbers the board positions like this at the start of a round:

```text
  1 | 2 | 3
 ---+---+---
  4 | 5 | 6
 ---+---+---
  7 | 8 | 9
```

Enter the number of an empty square when prompted. Get three of your symbols in a row, column, or diagonal to win.

## Repository layout

```text
.
├── chatbot.py
├── tictactoe.py
└── README.md
```
