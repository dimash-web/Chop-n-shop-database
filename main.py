import os
from dotenv import load_dotenv
import pymongo
import pandas as pd
import uuid

#setting up MongoDB and collections
load_dotenv()

mongodb_uri = os.getenv("MONGO_URI")
client = pymongo.MongoClient("mongodb_uri")
db = client["chop-n-shop"]
users_collection = db["users"]
stores_collection = db["stores"]
items_collection = db["items"]
recipes_collection = db["recipes"]

try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

#creating user documents
def add_user():

    #getting user inputs
    first_name = input("Enter first name: ")
    email = input("Enter email: ")
    budget = float(input("Enter budget: "))
    dietary_restrictions = input("Enter dietary restrictions (comma-seperated) or 'none' if none: ")
    allergies = input("Enter allergies (comma-separated) or 'none' if none: ")
    food_request = input("Enter food requests (comma-separated): ").split(",")
    preferred_stores = input("Enter preferred stores (comma-separated) or 'none' if none: ")
    
    #inserting into user documents
    user_document = {
        "First_name": first_name,
        "Email": email,
        "Budget": budget,
        "Dietary_restrictions":[] if dietary_restrictions.lower() == "none" else [dr.strip() for dr in dietary_restrictions.split(",")],
        "Allergies": [] if allergies.lower() == "none" else [a.strip() for a in allergies.split(",")],
        "Food_request": [f.strip() for f in food_request],
        "Preferred_stores": [] if preferred_stores.lower() == "none" else [s.strip() for s in preferred_stores.split(",")]
    }
    
    try:
        result = users_collection.insert_one(user_document)
        print(f"User {first_name} added with ID: {result.inserted_id}")
    except pymongo.errors.PyMongoError as e:
        print(f"An error occurred while adding the user: {e}")


# Creating store documents
def add_store():
    store_id = input("Enter store ID: ")
    name = input("Enter store name: ")
    item_id = input("Enter item ID: ")  # Changed to string
    item_name = input("Enter item name: ")

    # Inserting into store documents
    store_document = {
        "Store_id": store_id,
        "Name": name,
        "Item_id": item_id,
        "Item_name": item_name
    }

    try:
        result = stores_collection.insert_one(store_document)  # Correct collection reference
        print(f"Store {name} added with ID: {result.inserted_id}")
    except pymongo.errors.PyMongoError as e:
        print(f"An error occurred while adding the store: {e}")

#creating item documents
def add_item():
    #creating placeholder variables for now - to be scraped 
    item_id = str(uuid.uuid4())
    item_name = "Cheesecake"
    store_id = store['store_id']
    store_name = store['store_name']
    price = 6.99
    ingredients = ["cheese", "milk", "flour", "sugar"]
    calories = 360
    
    #creating item documents - to be scraped from stores 
    item_document = {
        "Item_id": item_id,
        "Item_name": item_name,
        "Store_id": store_id,
        "Store_name": store_name,
        "Price": price,
        "Ingredients": [i.strip() for i in ingredients],
        "Calories": calories
    }

    try:
        result = items_collection.insert_one(item_document)
        print(f"Item {item_name} added with ID: {result.inserted_id}")
    except pymongo.errors.PyMongoError as e:
        print(f"An error occurred while adding the item: {e}")

# Creating recipe documents
def add_recipe():
    # Getting recipe inputs
    recipe_id = input("Enter recipe ID: ")
    recipe_name = input("Enter recipe name: ")
    ingredients = input("Enter ingredients (comma-separated): ").split(",")

    # Inserting into recipe documents
    recipe_document = {
        "Recipe_id": recipe_id,
        "Recipe_name": recipe_name,
        "Ingredients": [i.strip() for i in ingredients]
    }

    try:
        result = recipes_collections.insert_one(recipe_document)
        print(f"Item {recipe_name} added with ID: {result.inserted_id}")
    except pymongo.errors.PyMongoError as e:
        print(f"An error occurred while adding the recipe: {e}")


#using pandas to export sample user data from db
def export_to_csv():
    users = list(users_collection.find())
    pd.DataFrame(users).to_csv('users_sample_data.csv', index=False)

    print("Sample data exported to CSV successfully.")

def main():
    add_user()
    add_store()
    add_item()
    add_recipe()
    export_to_csv()
    client.close()

if __name__ == "__main__":
    main()

