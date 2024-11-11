import os
from dotenv import load_dotenv
import pymongo
import pandas as pd
import uuid

# Load environment variables and connect to MongoDB
load_dotenv()

mongodb_uri = os.getenv("MONGO_URI")
client = pymongo.MongoClient(mongodb_uri)
db = client["chop-n-shop"]
users_collection = db["users"]
stores_collection = db["stores"]
items_collection = db["items"]
recipes_collection = db["recipes"]

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

# Creating store documents
def add_store():
    store_id = str(uuid.uuid4())
    name = input("Enter store name: ")

    # Inserting into store documents
    store_document = {
        "Store_id": store_id,
        "Name": name
    }

    try:
        result = stores_collection.insert_one(store_document)
        print(f"Store {name} added with ID: {result.inserted_id}")
    except pymongo.errors.PyMongoError as e:
        print(f"An error occurred while adding the store: {e}")

# Creating item documents from CSV
def upload_csv_to_items(file_path, store_name):
    # Load the CSV into a DataFrame
    df = pd.read_csv(file_path)

    # Rename 'Ounces' column to 'Amount'
    df.rename(columns={'Ounces': 'Amount'}, inplace=True)

    # Retrieve store info from the `stores` collection based on the store_name
    store = stores_collection.find_one({"Name": store_name})
    if not store:
        print(f"Store '{store_name}' not found in the database.")
        return

    store_id = store["Store_id"]  # Use the store's existing ID

    # Insert each row as a document in the `items` collection
    for _, row in df.iterrows():
        item_document = {
            "Item_id": str(uuid.uuid4()),  # Generate unique ID for each item
            "Item_name": row['Product'],
            "Store_id": store_id,
            "Store_name": store_name,
            "Price": row['Price'],
            "Amount": row['Amount'],  # Use 'Amount' instead of 'Ounces'
            "Serving_Size": row['Serving Size'],
            "Calories": row['Calories'],
            "Ingredients": row['Ingredients'].split(","),
            "Allergens": row['Allergens'].split(",") if pd.notna(row['Allergens']) else []
        }

        try:
            result = items_collection.insert_one(item_document)
            print(f"Item {row['Product']} added with ID: {result.inserted_id}")
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
        result = recipes_collection.insert_one(recipe_document)
        print(f"Recipe {recipe_name} added with ID: {result.inserted_id}")
    except pymongo.errors.PyMongoError as e:
        print(f"An error occurred while adding the recipe: {e}")

# Function to fix price field in existing items (convert string to float)
def update_prices_in_items():
    items = items_collection.find({"Price": {"$type": "string"}})  # Only items where Price is a string

    for item in items:
        try:
            # Clean the 'Price' field to remove any non-numeric characters (like '$')
            cleaned_price = item['Price'].replace('$', '').replace(',', '').strip()
            
            # Convert cleaned price to float
            updated_price = float(cleaned_price)
            
            # Update the item with the new price as a float
            items_collection.update_one(
                {"_id": item["_id"]},
                {"$set": {"Price": updated_price}}
            )
            print(f"Updated price for {item['Item_name']} to {updated_price}")
        except ValueError:
            print(f"Could not convert price for {item['Item_name']}: {item['Price']}")

# Export sample user data to CSV
def export_to_csv():
    users = list(users_collection.find())
    pd.DataFrame(users).to_csv('users_sample_data.csv', index=False)
    print("Sample data exported to CSV successfully.")

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
        print("8. Exit")

        choice = input("Enter your choice 1-8: ")

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
            file_path = "C:\\Users\\Sreya Mandalika\\coding-projects\\projects-in-programming\\trader-joes-scraping\\trader-joes-webscraping\\trader_joes_scraped_products.csv"
            store_name = input("Enter the store name for these items: ")
            upload_csv_to_items(file_path, store_name)
        elif choice == "7":
            update_prices_in_items()  # Option to update prices
        elif choice == "8":
            client.close()
            break
        else:
            print("Invalid choice. Please try again.")
    client.close()
    print("Closed")

if __name__ == "__main__":
    main()