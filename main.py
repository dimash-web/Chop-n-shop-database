import os
from dotenv import load_dotenv
import pymongo
import pandas as pd
import uuid
from bson import ObjectId

# Load environment variables and connect to MongoDB
load_dotenv()

mongodb_uri = os.getenv("MONGO_URI")
client = pymongo.MongoClient(mongodb_uri)
db = client["chop-n-shop"]
users_collection = db["users"]
stores_collection = db["stores"]
items_collection = db["items"]
recipes_collection = db["recipes"]
grocery_lists_collection = db["grocery_lists"]  # New collection for grocery lists

# Ping to check the connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

# Creating user documents
def add_user():
    # Getting user inputs
    first_name = input("Enter first name: ")
    email = input("Enter email: ")
    password = input("Enter password: ")
    budget = float(input("Enter budget: "))
    dietary_restrictions = input("Enter dietary restrictions (comma-separated) or 'none' if none: ")
    allergies = input("Enter allergies (comma-separated) or 'none' if none: ")
    food_request = input("Enter food requests (comma-separated): ").split(",")
    preferred_stores = input("Enter preferred stores (comma-separated) or 'none' if none: ")
    
    # Inserting into user documents
    user_document = {
        "First_name": first_name,
        "Email": email,
        "Password": password,
        "Budget": budget,
        "Dietary_restrictions": [] if dietary_restrictions.lower() == "none" else [dr.strip() for dr in dietary_restrictions.split(",")],
        "Allergies": [] if allergies.lower() == "none" else [a.strip() for a in allergies.split(",")],
        "Food_request": [f.strip() for f in food_request],
        "Preferred_stores": [] if preferred_stores.lower() == "none" else [s.strip() for s in preferred_stores.split(",")]
    }
    
    try:
        result = users_collection.insert_one(user_document)
        print(f"User {first_name} added with ID: {result.inserted_id}")
    except pymongo.errors.PyMongoError as e:
        print(f"An error occurred while adding the user: {e}")

# Creating a grocery list document without needing user_id explicitly
def create_grocery_list():
    # Fetch user data based on email
    email = input("Enter the user's email to create a grocery list: ")
    user = users_collection.find_one({"Email": email})
    if not user:
        print(f"User with email {email} not found.")
        return
    
    # Get food request and dietary restrictions
    food_request = user.get("Food_request", [])
    dietary_restrictions = user.get("Dietary_restrictions", [])
    allergies = user.get("Allergies", [])
    budget = user.get("Budget", 0)
    
    # Query for items that match the food request
    items = list(items_collection.find({"Item_name": {"$in": food_request}}))
    
    # Filter items based on dietary restrictions and allergies
    filtered_items = []
    for item in items:
        ingredients = item.get("Ingredients", [])
        if any(allergen in ingredients for allergen in allergies):
            continue
        if dietary_restrictions:
            if not any(dr in ingredients for dr in dietary_restrictions):
                continue
        filtered_items.append(item)
    
    # Ensure price is treated as a float and calculate total cost
    total_cost = 0
    for item in filtered_items:
        price = item.get('Price', 0)
        # Convert price to float if it's not already a float
        try:
            price = float(price)
        except ValueError:
            print(f"Warning: Invalid price for item {item['Item_name']}. Skipping.")
            continue
        total_cost += price
    
    # Check if filtered items match the budget
    if total_cost > budget:
        print(f"The total cost of the filtered items ({total_cost}) exceeds your budget ({budget}).")
        # Optionally, suggest cheaper alternatives here
    
    # Create the grocery list
    grocery_list = {
        "User_email": email,  # Store the user's email instead of user_id
        "Items": [{"Item_name": item["Item_name"], "Price": item["Price"]} for item in filtered_items],
        "Total_Cost": total_cost
    }
    
    # Insert the grocery list into the grocery_lists collection
    try:
        result = grocery_lists_collection.insert_one(grocery_list)
        print(f"Grocery list created with ID: {result.inserted_id}")
    except pymongo.errors.PyMongoError as e:
        print(f"An error occurred while creating the grocery list: {e}")


# Main menu
def main():
    while True:
        print("\nChoose an option:")
        print("1. Add User")
        print("2. Add Store")
        print("3. Add Item")
        print("4. Add Recipe")
        print("5. Export Users to CSV")
        print("6. Upload Items CSV to MongoDB")
        print("7. Update Prices in Items (Fix Existing Data)")
        print("8. Create Grocery List")
        print("9. Exit")

        choice = input("Enter your choice 1-9: ")

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
            file_path = input("Enter CSV file path: ")
            store_name = input("Enter store name: ")
            upload_csv_to_items(file_path, store_name)
        elif choice == "7":
            update_prices_in_items()
        elif choice == "8":
            create_grocery_list()  # No need for user_id
        elif choice == "9":
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
