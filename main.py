import os
import pymongo
import pandas as pd
import uuid
import pickle
from bson import ObjectId
from bson.binary import Binary
from dotenv import load_dotenv
from scipy.spatial.distance import cosine
from sentence_transformers import SentenceTransformer #using sentence transformers for embeddings

# Load environment variables and connect to MongoDB
load_dotenv()

mongodb_uri = os.getenv("MONGO_URI")
client = pymongo.MongoClient(mongodb_uri)
db = client["chop-n-shop"]
users_collection = db["users"]
stores_collection = db["stores"]
items_collection = db["items"]
recipes_collection = db["recipes"]
grocery_lists_collection = db["grocery_lists"] 

# initialize the sentence-transformers model --> this should be the most accurate model 
model = SentenceTransformer('all-MPNet-base-v2') 

# pinging to check the connection 
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

# function to generate embeddings for an item name (or description)
def generate_embedding(text):
    try:
        embedding = model.encode(text).tolist() # need to convert to list for Mongo
        return embedding
    except Exception as e:
        print(f"Error generating embedding for '{text}': {e}")
        return None

# function to update the items collection with embeddings
def add_embeddings_to_items():
    items = items_collection.find() 

    for item in items:
        item_name = item.get("Item_name")
        if item_name:
            # generate embedding for the item name
            embedding = generate_embedding(item_name)
            if embedding:
                item["embedding"] = Binary(pickle.dumps(embedding)) 

                # update the item document with the new embedding
                try:
                    items_collection.update_one(
                        {"_id": item["_id"]},
                        {"$set": {"embedding": item["embedding"]}}
                    )
                    print(f"Added embedding for item: {item_name}")
                except pymongo.errors.PyMongoError as e:
                    print(f"Error updating item {item_name}: {e}")

# function to calculate cosine similarity between two embeddings --> recced to use cosine
def calculate_similarity(embedding1, embedding2):
    return 1 - cosine(embedding1, embedding2)  

# function to search items based on a query
def search_items_by_query(query):
    query_embedding = generate_embedding(query)

    if query_embedding:
        items = items_collection.find()

        similar_items = []

        for item in items:
            # deserialize the embedding (binary -> list of floats)
            item_embedding = pickle.loads(item["embedding"])
            
            # calculate similarity between the query and the item embedding
            similarity_score = calculate_similarity(query_embedding, item_embedding)
            
            similar_items.append((item["Item_name"], similarity_score))

        # sort items by similarity (highest first)
        similar_items.sort(key=lambda x: x[1], reverse=True)

        # return the top *blank* most similar items --> can adjust if needed 
        return similar_items[:50]  
    else:
        print("Error generating query embedding.")
        return []

# creating user documents
def add_user():
    # getting user inputs
    first_name = input("Enter first name: ")
    email = input("Enter email: ")
    password = input("Enter password: ")
    budget = float(input("Enter budget: "))
    dietary_restrictions = input("Enter dietary restrictions (comma-separated) or 'none' if none: ")
    allergies = input("Enter allergies (comma-separated) or 'none' if none: ")
    food_request = input("Enter food requests (comma-separated): ").split(",")
    preferred_stores = input("Enter preferred stores (comma-separated) or 'none' if none: ")
    
    # inserting into user documents
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

# main menu
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
        print("9. Add Embeddings to Items")
        print("10. Search Items by Query")
        print("11. Exit")

        choice = input("Enter your choice 1-11: ")

        if choice == "1":
            add_user()
        elif choice == "9":
            add_embeddings_to_items()  
        elif choice == "10":
            query = input("Enter your search query: ")
            results = search_items_by_query(query)
            for item_name, score in results:
                print(f"Item: {item_name}, Similarity Score: {score}")
        elif choice == "11":
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
