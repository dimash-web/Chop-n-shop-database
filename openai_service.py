import openai
import os
from dotenv import load_dotenv
from pymongo import MongoClient
import pickle
from main import generate_embedding, calculate_similarity

# Load environment variables
load_dotenv(override=True)

# Set up OpenAI API key and MongoDB connection
openai.api_key = os.getenv("OPENAI_API_KEY")
mongodb_uri = os.getenv("MONGO_URI")
client = MongoClient(mongodb_uri)
db = client["chop-n-shop"]
items_collection = db["items"]

def generate_grocery_list(user_preferences):
    prepared_foods = []
    fresh_foods = []
    recipes = []
    total_cost = 0

    selected_categories = set()  # To ensure only one item per category
    selected_items = []  # List of selected items for grocery list

    # Handle Prepared Foods (e.g., pizza, chips)
    for food_request in user_preferences["Prepared_foods"]:
        # Search for one matching prepared food item
        query_results = search_items_by_query(food_request)

        for item_name, similarity_score in query_results:
            item = items_collection.find_one({"Item_name": item_name})
            if item and item.get("Category") not in selected_categories:
                item_price = item.get("Price")
                try:
                    item_price = float(item_price)
                except (TypeError, ValueError):
                    print(f"Skipping item: {item_name}, invalid Price: {item_price}")
                    continue

                if total_cost + item_price <= user_preferences["Budget"]:
                    prepared_foods.append(item)
                    selected_items.append(item)
                    selected_categories.add(item.get("Category"))
                    total_cost += item_price
                    break  # Only one item per category

    # Handle Fresh Foods (e.g., fruits, vegetables)
    for fresh_food in user_preferences["Fresh_foods"]:
        query_results = search_items_by_query(fresh_food)

        for item_name, similarity_score in query_results:
            item = items_collection.find_one({"Item_name": item_name})
            if item and item.get("Category") not in selected_categories:
                item_price = item.get("Price")
                try:
                    item_price = float(item_price)
                except (TypeError, ValueError):
                    print(f"Skipping item: {item_name}, invalid Price: {item_price}")
                    continue

                if total_cost + item_price <= user_preferences["Budget"]:
                    fresh_foods.append(item)
                    selected_items.append(item)
                    selected_categories.add(item.get("Category"))
                    total_cost += item_price

    # Handle Recipe Creation (if user requests recipes)
    if user_preferences.get("Recipes_to_make"):
        recipe_prompt = f"Based on the following ingredients: {', '.join(user_preferences['Recipes_to_make'])}, generate a simple recipe with quantities."
        recipe_response = openai.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": recipe_prompt}],
            max_tokens=300,
            temperature=0.7
        )
        recipes = recipe_response.choices[0].message.content.strip()

    # Format grocery list
    formatted_grocery_lists = "Prepared Foods:\n"
    for item in prepared_foods:
        formatted_grocery_lists += f"{item['Item_name']}, {item.get('Quantity', '1')} {item.get('Measurement', 'unit')}, ${item['Price']}\n"
    formatted_grocery_lists += "\nFresh Foods:\n"
    for item in fresh_foods:
        formatted_grocery_lists += f"{item['Item_name']}, {item.get('Quantity', '1')} {item.get('Measurement', 'unit')}, ${item['Price']}\n"

    formatted_grocery_lists += f"\nRemaining Budget: ${user_preferences['Budget'] - total_cost:.2f}\n"

    return formatted_grocery_lists, recipes

def search_items_by_query(query):
    query_embedding = generate_embedding(query)
    items = items_collection.find()

    similar_items = []
    for item in items:
        item_embedding = pickle.loads(item["embedding"])
        similarity_score = calculate_similarity(query_embedding, item_embedding)
        similar_items.append((item["Item_name"], similarity_score))

    similar_items.sort(key=lambda x: x[1], reverse=True)
    return similar_items[:5]  # Return top 5 similar items

# Example usage
user_preferences = {
    "Budget": 50,
    "Prepared_foods": ["pizza", "chips", "frozen curry"],  # Prepared foods user wants
    "Fresh_foods": ["milk", "apples", "bananas", "lettuce"],  # Fresh foods user wants
    "Recipes_to_make": ["pasta"],  # Recipes user wants to make
}

# Generate and display grocery list and recipes
grocery_list, recipes = generate_grocery_list(user_preferences)
print("Grocery List:\n", grocery_list)
print("\nRecipes:\n", recipes)
