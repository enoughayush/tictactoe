"""A simple rule-based chatbot using if/elif statements."""


def get_response(message):
    """Return a response based on simple keyword and phrase rules."""
    text = message.strip().lower()

    if text in {"hi", "hello", "hey", "hey there"}:
        return "Hello! How can I help you?"
    elif "how are you" in text:
        return "I'm doing well, thanks for asking! How can I help?"
    elif "your name" in text or text == "name":
        return "I'm ChatBot, a simple rule-based chatbot."
    elif "help" in text:
        return "You can say hello, ask how I am, ask my name, or say bye."
    elif "thank" in text:
        return "You're welcome!"
    elif text in {"bye", "goodbye", "exit", "quit"}:
        return "Goodbye! It was nice chatting with you."
    else:
        return "I'm not sure how to respond to that yet. Try asking for help."


def main():
    print("ChatBot: Hello! Type 'help' to see what I can respond to, or 'bye' to exit.")

    while True:
        user_input = input("You: ").strip()
        if not user_input:
            print("ChatBot: Please type something so I can respond.")
            continue

        response = get_response(user_input)
        print(f"ChatBot: {response}")

        if user_input.lower() in {"bye", "goodbye", "exit", "quit"}:
            break


if __name__ == "__main__":
    main()
