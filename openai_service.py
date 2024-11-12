import openai
import os
from dotenv import load_dotenv
from pymongo import MongoClient
import random

# Load environment variables
load_dotenv()

# Set up OpenAI API key and MongoDB connection
openai.api_key = os.getenv("OPENAI_API_KEY")
mongodb_uri = os.getenv("MONGO_URI")
client = MongoClient(mongodb_uri)
db = client["chop-n-shop"]
items_collection = db["items"]

def generate_grocery_list(user_preferences):
    query = {
        "Store_name": {"$in": user_preferences["Preferred_stores"]} if user_preferences["Preferred_stores"] else {},
        "Ingredients": {"$nin": user_preferences["Allergies"]},
        "Price": {"$lte": user_preferences["Budget"]}
    }
    if user_preferences.get("Food_type"):
        query["Food_type"] = {"$in": user_preferences["Food_type"]}

    items = list(items_collection.find(query, {
        "_id": 0, "Item_name": 1, "Price": 1, "Calories": 1, "Ingredients": 1,
        "Store_name": 1, "Food_type": 1, "Quantity": 1, "Measurement": 1
    }))

    if not items:
        return "No items found matching your preferences."

    random.shuffle(items)
    selected_items = []
    total_cost = 0
    for item in items:
        if total_cost + item['Price'] > user_preferences["Budget"]:
            break
        selected_items.append(item)
        total_cost += item['Price']

    store_items = {}
    for item in selected_items:
        store_name = item["Store_name"]
        if store_name not in store_items:
            store_items[store_name] = []
        store_items[store_name].append(item)

    formatted_grocery_lists = ""
    remaining_budget = user_preferences["Budget"] - total_cost
    for store, items in store_items.items():
        formatted_grocery_lists += f"{store}:\n"
        for item in items:
            formatted_grocery_lists += f"{item['Item_name']}, {item.get('Quantity', '1')} {item.get('Measurement', 'unit')}, ${item['Price']}\n"
        formatted_grocery_lists += f"\nTotal for {store}: ${total_cost:.2f}\n"

    formatted_grocery_lists += f"\nRemaining Budget: ${remaining_budget:.2f}\n"

    # Generate recipes based on the grocery list
    ingredient_list = "\n".join([item["Item_name"] for item in selected_items])
    recipe_prompt = f"""
    Based on the following grocery list:
    {ingredient_list}
    
    Create 3 unique recipes that use only these ingredients and serve 2 people each. 
    Specify exact measurements and keep recipes brief.
    """

    recipe_response = openai.chat.completions.create(
        model="gpt-4.0-mini",
        messages=[{"role": "system", "content": "Generate recipes based only on the provided ingredients."},
                  {"role": "user", "content": recipe_prompt}],
        max_tokens=300,
        temperature=0.5
    )

    recipes = recipe_response.choices[0].message.content.strip()
    
    return formatted_grocery_lists, recipes

# Example usage
user_preferences = {
    "Budget": 50,
    "Allergies": ["peanuts", "shellfish"],
    "Preferred_stores": ["Trader Joe's"]
}

# Generate and display grocery list and recipes
grocery_list, recipes = generate_grocery_list(user_preferences)
print("Grocery List:\n", grocery_list)
print("\nRecipes:\n", recipes)
