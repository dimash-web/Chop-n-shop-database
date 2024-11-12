from fastapi import FastAPI, HTTPException
from main import users_collection, stores_collection, items_collection, recipes_collection
from pydantic import BaseModel
from bson import ObjectId
import uuid
from fastapi.middleware.cors import CORSMiddleware
import re

app = FastAPI()

# Allow all origins (or specify allowed origins in a list)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # or specify origins like ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


class LoginUser(BaseModel):
    email: str
    password: str


# define the pydantic models for input validation
class Item(BaseModel):
    Item_name: str
    Store_name: str
    Price: float
    Ingredients: list[str]
    Calories: int

class User(BaseModel):
    first_name: str
    email: str
    password: str
    allergies: str

class Store(BaseModel):
    name: str

class Recipe(BaseModel):
    Recipe_id: str
    Recipe_name: str
    Ingredients: list[str]

#endpoint to get recipe by name
@app.get("/recipes/{recipe_name}")
async def get_recipe(recipe_name: str):
    # Perform a case-insensitive search using regex
    recipe = recipes_collection.find_one({"Recipe_name": {"$regex": f"^{re.escape(recipe_name)}$", "$options": "i"}})
    if recipe:
        # Convert ObjectId to string for returning to the user
        recipe["_id"] = str(recipe["_id"])  # Convert ObjectId to string
        return {
            "Recipe_id": recipe.get("Recipe_id", ""),
            "Recipe_name": recipe.get("Recipe_name", ""),
            "Ingredients": recipe.get("Ingredients", []),
            "_id": recipe["_id"]
        }
    raise HTTPException(status_code=404, detail="Recipe not found")

# endpoint to get all items
@app.get("/items/")
async def get_items():
    items = list(items_collection.find({}, {"_id": 0}))
    return items

# endpoint to get a specific item by ID
@app.get("/items/{item_id}")
async def get_item(item_id: str):
    item = items_collection.find_one({"_id": ObjectId(item_id)})
    if item:
        item["_id"] = str(item["_id"])  
        return item
    raise HTTPException(status_code=404, detail="Item not found")

# endpoint to create a new item
@app.post("/items/")
async def create_item(item: Item):
    item_document = item.dict()
    item_document["Item_id"] = str(uuid.uuid4())
    items_collection.insert_one(item_document)
    return {"message": "Item created successfully", "Item_id": item_document["Item_id"]}

# endpoint to update an item by ID
@app.put("/items/{item_id}")
async def update_item(item_id: str, item: Item):
    update_result = items_collection.update_one({"_id": ObjectId(item_id)}, {"$set": item.dict()})
    if update_result.matched_count == 1:
        return {"message": "Item updated successfully"}
    raise HTTPException(status_code=404, detail="Item not found")

# endpoint to delete an item by ID
@app.delete("/items/{item_id}")
async def delete_item(item_id: str):
    delete_result = items_collection.delete_one({"_id": ObjectId(item_id)})
    if delete_result.deleted_count == 1:
        return {"message": "Item deleted successfully"}
    raise HTTPException(status_code=404, detail="Item not found")

# endpoint to generate a grocery list based on user preferences
# @app.post("/generate_grocery_list/")
# async def generate_grocery_list_endpoint(user_id: str):
#     user = users_collection.find_one({"_id": ObjectId(user_id)})
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")

#     # prepare user preferences to pass to the OpenAI function
#     user_preferences = {
#         "Budget": user["Budget"],
#         "Dietary_restrictions": user["Dietary_restrictions"],
#         "Allergies": user["Allergies"],
#         "Food_request": user["Food_request"],
#         "Preferred_stores": user["Preferred_stores"]
#     }

#     # Generate grocery list using the OpenAI API
#     grocery_list = generate_grocery_list(user_preferences)
    
#     return {"grocery_list": grocery_list}

# endpoint to add user to the database
@app.post("/register/")
async def add_user(user: User):
    # dietary_restrictions = [] if not user.dietary_restrictions or user.dietary_restrictions.lower() == "none" else user.dietary_restrictions.split(",")
    allergies = [] if not user.allergies or user.allergies.lower() == "none" else user.allergies.split(",")
    # food_request = [] if not user.food_request or user.food_request.lower() == "none" else user.food_request.split(",")
    # preferred_stores = [] if not user.preferred_stores or user.preferred_stores.lower() == "none" else user.preferred_stores.split(",")

    user_document = {
        "first_name": user.first_name,
        "email": user.email,
        "password": user.password,
        # "dietary_restrictions": dietary_restrictions,
        "allergies": allergies,
        # "food_request": food_request,
        # "preferred_stores": preferred_stores,
    }

    try:
        result = users_collection.insert_one(user_document)
        return {"message": f"User {user.first_name} added with ID: {result.inserted_id}"}
    except Exception as e:
        return {"error": f"An error occurred while adding the user: {str(e)}"}

@app.post("/login/")
async def login(user: LoginUser):
    # Find user by email
    existing_user = users_collection.find_one({"email": user.email})

    # Check if user exists and the password matches
    if existing_user and existing_user["password"] == user.password:
        return {"message": "Login successful"}
    else:
        raise HTTPException(status_code=401, detail="Invalid email or password")

# retrieving the users
@app.get("/users/")
async def get_users():
    users = list(users_collection.find({}))
    for user in users:
        user["_id"] = str(user["_id"]) 
    return users


# retrieving the user data by id 
@app.get("/users/{user_id}")
async def get_user(user_id: str):
    user = users_collection.find_one({"_id": ObjectId(user_id)})
    if user:
        user["_id"] = str(user["_id"])
        return user
    raise HTTPException(status_code=404, detail="User not found")

# endpoint to add a store to the database
@app.post("/add_store/")
async def add_store(store: Store):
    store_id = str(uuid.uuid4())
    store_document = {
        "Store_id": store_id,
        "Name": store.name
    }

    try:
        result = stores_collection.insert_one(store_document)
        return {"message": f"Store {store.name} added with ID: {result.inserted_id}"}
    except Exception as e:
        return {"error": f"An error occurred while adding the store: {str(e)}"}

# Endpoint to retrieve the grocery list for a user
@app.get("/users/{user_id}/grocery-list/")
async def get_grocery_list(user_id: str):
    user = users_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user.get("grocery_list", [])


# Optional: Endpoint to delete a grocery item from the list
@app.delete("/users/{user_id}/grocery-list/{item_id}")
async def delete_grocery_item(user_id: str, item_id: str):
    user = users_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    update_result = users_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$pull": {"grocery_list": {"item_id": item_id}}}
    )

    if update_result.modified_count == 1:
        return {"message": "Grocery item deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Grocery item not found")



