"""Predefined-Rules Chatbot: an offline, rule-based conversational program."""

import ast
from collections import Counter
from math import log, sqrt
import operator
import random
import re
from datetime import datetime
from typing import Union

Number = Union[int, float]

# Arithmetic is limited to these operations; user input is never passed to eval().
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

EXIT_COMMANDS = {"bye", "goodbye", "see you", "exit", "quit"}
CAPITALS = {
    "france": "Paris",
    "india": "New Delhi",
    "japan": "Tokyo",
    "italy": "Rome",
    "canada": "Ottawa",
}
JOKES = (
    "Why did the computer go to the doctor? It had a virus!",
    "Why was the math book sad? It had too many problems.",
    "Why do programmers prefer dark mode? Because light attracts bugs!",
)


# Lightweight FAQ retrieval adds basic NLP without downloading a language model.
FAQS = (
    ("what is artificial intelligence ai", "AI is software that performs tasks such as recognizing patterns, making predictions, or understanding language."),
    ("what is machine learning", "Machine learning is a way for computers to learn patterns from examples instead of following only hand-written rules."),
    ("what is deep learning neural network", "Deep learning uses layered neural networks to learn patterns from data, often for images, speech, and text."),
    ("what is image captioning", "Image captioning combines computer vision and language generation to describe an image in words."),
    ("what is a recommendation system", "A recommendation system suggests items using preferences, item similarities, or patterns in other users' choices."),
    ("what is minimax tic tac toe", "Minimax searches possible moves and assumes both players choose well. In tic-tac-toe it can guarantee at least a draw."),
    ("how can i learn python programming coding", "Start with variables, conditions, loops, and functions. Then build small projects and read the errors when something breaks."),
    ("how can i study prepare for an exam", "Break the material into small topics, practise recalling it without notes, and take short breaks between focused sessions."),
    ("how do i choose a movie recommendation", "A content-based recommender compares item features, such as movie genres, with the preferences you give it."),
    ("why does an ai model make mistakes", "AI models learn from limited examples and can miss context or reflect gaps in their data. Check important answers against reliable sources."),
)

_STOP_WORDS = {"a", "an", "and", "are", "can", "do", "does", "for", "how", "i", "is", "it", "me", "my", "of", "please", "tell", "the", "to", "what", "with", "you"}
_SYNONYMS = {
    "artificial": "ai", "intelligence": "ai", "machine": "ml",
    "learning": "learn", "studying": "study", "programming": "coding",
    "code": "coding", "pictures": "image", "photos": "image",
    "captions": "caption", "movies": "movie", "recommendations": "recommendation",
    "networks": "network", "models": "model", "mistakes": "mistake",
}


def _tokens(text: str) -> set[str]:
    """Normalize a sentence into useful words for FAQ matching."""
    words = re.findall(r"[a-z0-9]+", text.lower())
    return {_SYNONYMS.get(word, word) for word in words if word not in _STOP_WORDS}


def find_faq_answer(message: str) -> str | None:
    """Return the closest FAQ answer when its TF-IDF overlap is strong enough."""
    query = _tokens(message)
    if not query:
        return None
    documents = [_tokens(question) for question, _ in FAQS]
    document_frequency = Counter(word for document in documents for word in document)
    count = len(documents)
    best_score = 0.0
    best_answer = None

    for (_, answer), document in zip(FAQS, documents):
        weights = {
            word: 1.0 + log((count + 1) / (document_frequency[word] + 1))
            for word in query | document
        }
        shared = query & document
        dot = sum(weights[word] ** 2 for word in shared)
        query_norm = sum(weights[word] ** 2 for word in query)
        document_norm = sum(weights[word] ** 2 for word in document)
        score = dot / sqrt(query_norm * document_norm) if query_norm and document_norm else 0.0
        if score > best_score:
            best_score, best_answer = score, answer

    return best_answer if best_score >= 0.38 else None

def calculate(expression: str) -> Number:
    """Safely evaluate a basic arithmetic expression."""
    if len(expression) > 50:
        raise ValueError("That calculation is too long.")

    tree = ast.parse(expression, mode="eval")

    def evaluate(node: ast.AST) -> Number:
        if isinstance(node, ast.Expression):
            return evaluate(node.body)
        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
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


def get_response(message: str) -> str:
    """Return a response based on the message and the chatbot's rules."""
    text = message.strip().lower()
    if not text:
        return "Please type a message so I can respond."
    if text in EXIT_COMMANDS:
        return "Goodbye! It was nice chatting with you."

    # Accept simple expressions such as "12 * (3 + 2)".
    if re.fullmatch(r"[\d\s().+\-*/%]+", text) and re.search(r"\d", text):
        try:
            result = calculate(text)
            return f"The answer is {result:g}." if isinstance(result, float) else f"The answer is {result}."
        except (SyntaxError, ValueError, ZeroDivisionError, OverflowError):
            return "I couldn't calculate that. Try an expression like 12 * (3 + 2)."

    if re.search(r"\b(hi|hello|hey|good morning|good afternoon|good evening)\b", text):
        return "Hello! What would you like to talk about?"
    if re.search(r"\bhow are you\b", text):
        return "I'm doing well, thanks for asking. What can I help with?"
    if re.search(r"\b(your name|who are you)\b", text):
        return "I'm ChatBot, an offline assistant with rules and lightweight FAQ matching."
    if re.search(r"\bwhat can you do\b|\bhelp\b", text):
        return (
            "I can answer common AI and programming questions, tell a joke, share capitals, "
            "give the date or time, and calculate basic math."
        )
    if re.search(r"\b(thank you|thanks|thx)\b", text):
        return "You're welcome!"
    if re.search(r"\b(joke|make me laugh)\b", text):
        return random.choice(JOKES)
    if re.search(r"\b(time|what time)\b", text):
        return f"The time is {datetime.now().strftime('%I:%M %p')} on this computer."
    if re.search(r"\b(date|what day|today)\b", text):
        return f"Today is {datetime.now().strftime('%A, %B %d, %Y')}."
    if re.search(r"\b(weather|forecast)\b", text):
        return "I work offline, so I can't check live weather."
    if re.search(r"\b(sad|unhappy|upset|lonely|bad day)\b", text):
        return "I'm sorry you're having a hard time. Would you like to tell me more?"
    if re.search(r"\b(happy|excited|great day)\b", text):
        return "That's great to hear! What made your day good?"
    faq_answer = find_faq_answer(text)
    if faq_answer:
        return faq_answer

    if re.search(r"\b(study|studying|exam|homework)\b", text):
        return "Try studying in short sessions with small breaks. What subject are you working on?"
    if re.search(r"\b(python|programming|coding)\b", text):
        return (
            "Python is a programming language. I can calculate basic math and respond "
            "to a few predefined programming topics."
        )

    capital_match = re.search(
        r"\bcapital of (france|india|japan|italy|canada)\b", text
    )
    if capital_match:
        country = capital_match.group(1)
        return f"The capital of {country.title()} is {CAPITALS[country]}."

    return (
        "I don't have a rule for that yet, and I work offline. "
        "Try rephrasing, or type help for examples."
    )


def main() -> None:
    """Run the chatbot in an interactive terminal session."""
    print("=" * 52)
    print("              LOCAL NLP CHATBOT")
    print("=" * 52)
    print("Type 'help' to see what I can do, or 'bye' to exit.\n")

    while True:
        try:
            user_input = input("You: ").strip()
        except EOFError:
            print("\nChatBot: Session ended. Goodbye!")
            break

        response = get_response(user_input)
        print(f"ChatBot: {response}\n")
        if user_input.lower() in EXIT_COMMANDS:
            break


if __name__ == "__main__":
    main()




