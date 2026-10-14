"""A simple product recommendation system using shared product features.

Run with:
    py recommendationsystem.py

Type one or more product names from the catalog, separated by commas.
"""

import tkinter as tk
from tkinter import messagebox

# Each product has a few features used to find similar products.
PRODUCTS = {
    "Wireless Headphones": ["audio", "wireless", "travel", "entertainment"],
    "Bluetooth Speaker": ["audio", "wireless", "portable", "entertainment"],
    "E-reader": ["reading", "books", "portable", "travel"],
    "Tablet": ["electronics", "reading", "portable", "work"],
    "Laptop Stand": ["computer", "desk", "work", "ergonomic"],
    "Mechanical Keyboard": ["computer", "desk", "work", "gaming"],
    "Wireless Mouse": ["computer", "desk", "work", "portable"],
    "Webcam": ["computer", "work", "video", "accessories"],
    "Smart Watch": ["fitness", "wearable", "health", "notifications"],
    "Fitness Tracker": ["fitness", "wearable", "health", "running"],
    "Running Shoes": ["fitness", "running", "outdoors", "clothing"],
    "Yoga Mat": ["fitness", "exercise", "home", "wellness"],
    "Coffee Maker": ["kitchen", "coffee", "home", "appliances"],
    "Air Fryer": ["kitchen", "cooking", "home", "appliances"],
    "Reusable Water Bottle": ["fitness", "travel", "reusable", "outdoors"],
    "Backpack": ["travel", "school", "storage", "outdoors"],
    "Desk Lamp": ["desk", "home", "lighting", "work"],
    "Power Bank": ["portable", "travel", "electronics", "charging"],
}


def recommend_products(liked_products, number_of_recommendations=5):
    """Return products that share the most features with the user's choices."""
    feature_preferences = {}

    for product in liked_products:
        for feature in PRODUCTS[product]:
            feature_preferences[feature] = feature_preferences.get(feature, 0) + 1

    scores = {}
    for product, features in PRODUCTS.items():
        if product in liked_products:
            continue

        score = sum(feature_preferences.get(feature, 0) for feature in features)
        if score > 0:
            scores[product] = score

    ranked_products = sorted(scores, key=scores.get, reverse=True)
    return ranked_products[:number_of_recommendations]


def show_recommendations():
    """Check the typed product names and display similar products."""
    typed_names = [name.strip() for name in product_entry.get().split(",") if name.strip()]
    if not typed_names:
        messagebox.showinfo("Enter a product", "Type at least one product name first.")
        return

    # Ignore capitalization differences and use the catalog's spelling.
    catalog_names = {name.lower(): name for name in PRODUCTS}
    liked_products = []
    unknown_names = []
    for name in typed_names:
        product_name = catalog_names.get(name.lower())
        if product_name is None:
            unknown_names.append(name)
        elif product_name not in liked_products:
            liked_products.append(product_name)

    if unknown_names:
        messagebox.showerror(
            "Product not in catalog",
            "I couldn't find: " + ", ".join(unknown_names)
            + "\nUse a product name shown in the catalog list.",
        )
        return

    suggestions = recommend_products(liked_products)
    recommendation_list.delete(0, tk.END)
    if not suggestions:
        recommendation_list.insert(tk.END, "No similar products found.")
        return

    for product in suggestions:
        features = ", ".join(PRODUCTS[product])
        recommendation_list.insert(tk.END, f"{product} ({features})")


# Create a basic window for entering preferences and viewing suggestions.
window = tk.Tk()
window.title("Product Recommendation System")
window.geometry("650x720")

heading = tk.Label(window, text="Product Recommendation System", font=("Arial", 18, "bold"))
heading.pack(pady=(16, 6))

instructions = tk.Label(
    window,
    text="Type products you like, separated by commas. Suggestions use shared features.",
    wraplength=580,
)
instructions.pack(pady=(0, 10))

product_entry = tk.Entry(window, width=68)
product_entry.pack(padx=20, pady=(0, 4), fill="x")
tk.Label(window, text="Example: Wireless Mouse, Mechanical Keyboard", fg="gray").pack(
    anchor="w", padx=22, pady=(0, 6)
)

catalog_heading = tk.Label(window, text="Products you can enter:", font=("Arial", 11, "bold"))
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
for product_name in PRODUCTS:
    catalog_list.insert(tk.END, product_name)
catalog_list.configure(state=tk.DISABLED)

recommend_button = tk.Button(
    window, text="Get Recommendations", command=show_recommendations, padx=12, pady=6
)
recommend_button.pack(pady=10)

results_heading = tk.Label(window, text="Recommended products:", font=("Arial", 12, "bold"))
results_heading.pack(anchor="w", padx=25)

recommendation_list = tk.Listbox(window, height=7, width=60)
recommendation_list.pack(padx=20, pady=(5, 15), fill="both", expand=True)

window.mainloop()
