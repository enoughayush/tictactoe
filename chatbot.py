"""An offline chatbot that responds using predefined rules."""

import ast
import operator
import random
import re
from datetime import datetime


# Only these arithmetic operations are allowed by the calculator.
_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def calculate(expression):
    """Safely calculate a basic arithmetic expression without using eval()."""
    if len(expression) > 50:
        raise ValueError("That calculation is too long.")

    tree = ast.parse(expression, mode="eval")

    def evaluate(node):
        if isinstance(node, ast.Expression):
            return evaluate(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        if isinstance(node, ast.BinOp) and type(node.op) in _OPERATORS:
            left = evaluate(node.left)
            right = evaluate(node.right)
            if isinstance(node.op, ast.Pow) and abs(right) > 8:
                raise ValueError("Please keep exponents at 8 or below.")
            result = _OPERATORS[type(node.op)](left, right)
            if abs(result) > 1_000_000_000_000:
                raise ValueError("That result is too large.")
            return result
        if isinstance(node, ast.UnaryOp) and type(node.op) in _OPERATORS:
            return _OPERATORS[type(node.op)](evaluate(node.operand))
        raise ValueError("Use numbers and basic arithmetic operators only.")

    return evaluate(tree)


def get_response(message):
    """Choose a response from predefined rules based on the user's message."""
    text = message.strip().lower()
    if not text:
        return "Please type a message so I can respond."

    # Match a basic arithmetic expression, such as "12 * (3 + 2)".
    if re.fullmatch(r"[\d\s().+\-*/%]+", text) and re.search(r"\d", text):
        try:
            result = calculate(text)
            return f"The answer is {result:g}." if isinstance(result, float) else f"The answer is {result}."
        except (SyntaxError, ValueError, ZeroDivisionError, OverflowError):
            return "I couldn't calculate that. Try an expression like 12 * (3 + 2)."

    if re.search(r"\b(hi|hello|hey|good morning|good afternoon|good evening)\b", text):
        return "Hello! What would you like to talk about?"
    elif re.search(r"\bhow are you\b", text):
        return "I'm doing well, thanks for asking! What can I help with?"
    elif re.search(r"\b(your name|who are you)\b", text):
        return "I'm ChatBot, an offline chatbot that uses predefined rules."
    elif re.search(r"\bwhat can you do\b|\bhelp\b", text):
        return (
            "I can chat about greetings, feelings, jokes, studying, and basic Python; "
            "share a few facts; tell you the date or time; and calculate basic math."
        )
    elif re.search(r"\b(thank you|thanks|thx)\b", text):
        return "You're welcome!"
    elif re.search(r"\b(bye|goodbye|see you|exit|quit)\b", text):
        return "Goodbye! It was nice chatting with you."
    elif re.search(r"\b(joke|make me laugh)\b", text):
        return random.choice([
            "Why did the computer go to the doctor? It had a virus!",
            "Why was the math book sad? It had too many problems.",
            "Why do programmers prefer dark mode? Because light attracts bugs!",
        ])
    elif re.search(r"\b(time|what time)\b", text):
        return f"The time is {datetime.now().strftime('%I:%M %p')} on this computer."
    elif re.search(r"\b(date|what day|today)\b", text):
        return f"Today is {datetime.now().strftime('%A, %B %d, %Y')}."
    elif re.search(r"\b(weather|forecast)\b", text):
        return "I work offline, so I can't check live weather."
    elif re.search(r"\b(sad|unhappy|upset|lonely|bad day)\b", text):
        return "I'm sorry you're having a hard time. Want to tell me a little more?"
    elif re.search(r"\b(happy|excited|great day)\b", text):
        return "That's great to hear! What made your day good?"
    elif re.search(r"\b(study|studying|exam|homework)\b", text):
        return "Try studying in short sessions with small breaks. What subject are you working on?"
    elif re.search(r"\b(python|programming|coding)\b", text):
        return "Python is a programming language. I can help with simple arithmetic, but I only know a few predefined coding replies."
    elif re.search(r"\b(capital of france|capital of india|capital of japan|capital of italy|capital of canada)\b", text):
        if "france" in text:
            return "The capital of France is Paris."
        if "india" in text:
            return "The capital of India is New Delhi."
        if "japan" in text:
            return "The capital of Japan is Tokyo."
        if "italy" in text:
            return "The capital of Italy is Rome."
        return "The capital of Canada is Ottawa."

    return (
        "I don't have a rule for that yet, and I work offline. "
        "Try asking for help, a joke, the date or time, a capital, or a math calculation."
    )


def main():
    print("ChatBot: Hi! Type 'help' to see what I can do, or 'bye' to exit.")

    while True:
        user_input = input("You: ").strip()
        response = get_response(user_input)
        print(f"ChatBot: {response}")

        if user_input.lower() in {"bye", "goodbye", "see you", "exit", "quit"}:
            break


if __name__ == "__main__":
    main()
