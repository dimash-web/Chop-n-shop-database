import os
from dotenv import load_dotenv
import pymongo

#setting up MongoDB and collections
load_dotenv()

mongodb_uri = os.getenv("MONGO_URI")
client = pymongo.MongoClient(mongodb_uri)
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

#creating store documents

#creating item documents

#creating recipe documents

def main():
    add_user()
    client.close()

if __name__ == "__main__":
    main()
