import os
from dotenv import load_dotenv
import pymongo
import pandas as pd
import uuid

#setting up MongoDB and collections
load_dotenv()

mongodb_uri = os.getenv("MONGO_URI")

client = pymongo.MongoClient(mongodb_uri)
print(client)
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
    inserted_user = users_collection.find_one({"_id": result.inserted_id})
    print(inserted_user)


# Creating store documents
def add_store():
    store_id = str(uuid.uuid4())
    name = input("Enter store name: ")

    # Inserting into store documents
    store_document = {
        "Store_id": store_id,
        "Name": name,
    
    }

    try:
        result = stores_collection.insert_one(store_document)  # Correct collection reference
        print(f"Store {name} added with ID: {result.inserted_id}")
    except pymongo.errors.PyMongoError as e:
        print(f"An error occurred while adding the store: {e}")

#creating item documents
def add_item():
    
    item_id = str(uuid.uuid4())
    item_name = input("Enter item name: ")
    store_id = input("Enter store ID: ")
    store_name = input("Enter store name: ")
    price = input("Enter item price: ")
    ingredients = input("Enter ingredients (comma-separated): ").split(",")
    calories = input("Enter calories: ")
    
    
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
    recipe_id = str(uuid.uuid4())
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
 
    while True:
        print("\nChoose an option:")
        print("1. Add User")
        print("2. Add Store")
        print("3. Add Item")
        print("4. Add Recipe")
        print("5. Export Users to CSV")
        print("6. Exit")

        choice = input("Enter your choice 1-6: ")

        if choice == "1":
            add_user()
        elif choice == "2":
            add_store()
        elif choice == "3":
            add_item()
        elif choice == "4":
            add_recipe()
        elif choice == "5":
            export_to_csv()
        elif choice == "6":
            client.close()
            break
        else:
            print("Invalid choice. Please try again.")
    client.close()
    print("Closed")

if __name__ == "__main__":
    main()
