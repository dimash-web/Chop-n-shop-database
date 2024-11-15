import openai
import os
from dotenv import load_dotenv
from pymongo import MongoClient
import random
import pickle 
from scipy.spatial.distance import cosine
from main import generate_embedding, calculate_similarity

# Load environment variables
load_dotenv()

# Set up OpenAI API key and MongoDB connection
openai.api_key = os.getenv("OPENAI_API_KEY")
mongodb_uri = os.getenv("MONGO_URI")
client = MongoClient(mongodb_uri)
db = client["chop-n-shop"]
items_collection = db["items"]

# Function to generate a grocery list
def generate_grocery_list(user_preferences):
    selected_items = []
    total_cost = 0

    for food_request in user_preferences["Food_request"]:
        # Search for items related to the user's food request
        query_results = search_items_by_query(food_request)
        
        for item_name, similarity_score in query_results:
            item = items_collection.find_one({"Item_name": item_name})
            if item and total_cost + item['Price'] <= user_preferences["Budget"]:
                selected_items.append(item)
                total_cost += item['Price']

    # Group selected items by store
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

    recipe_response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "system", "content": "Generate recipes based only on the provided ingredients."},
                  {"role": "user", "content": recipe_prompt}],
        max_tokens=300,
        temperature=0.5
    )

    recipes = recipe_response.choices[0].message.content.strip()
    
    return formatted_grocery_lists, recipes

# Example search function using embeddings
def search_items_by_query(query):
    query_embedding = generate_embedding(query)
    items = items_collection.find()

    similar_items = []
    for item in items:
        item_embedding = pickle.loads(item["embedding"])
        similarity_score = calculate_similarity(query_embedding, item_embedding)
        similar_items.append((item["Item_name"], similarity_score))

    similar_items.sort(key=lambda x: x[1], reverse=True)
    return similar_items[:10]  # Adjust this number as needed

# Example usage
user_preferences = {
    "Budget": 50,
    "Allergies": ["peanuts", "shellfish"],
    "Preferred_stores": ["Trader Joe's"],
    "Food_request": ["pizza", "Indian food", "chips"]
}

# Generate and display grocery list and recipes
grocery_list, recipes = generate_grocery_list(user_preferences)
print("Grocery List:\n", grocery_list)
print("\nRecipes:\n", recipes)
