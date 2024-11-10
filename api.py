from fastapi import FastAPI, HTTPException
from main import users_collection, items_collection
from openai_service import generate_grocery_list  # Import the OpenAI function
from pydantic import BaseModel
from bson import ObjectId
import uuid

app = FastAPI()

# Define Item model
class Item(BaseModel):
    Item_name: str
    Store_name: str
    Price: float
    Ingredients: list[str]
    Calories: int

# Endpoint to get all items
@app.get("/items/")
async def get_items():
    items = list(items_collection.find({}, {"_id": 0}))
    return items

# Endpoint to get a specific item by ID
@app.get("/items/{item_id}")
async def get_item(item_id: str):
    item = items_collection.find_one({"_id": ObjectId(item_id)})
    if item:
        item["_id"] = str(item["_id"])  
        return item
    raise HTTPException(status_code=404, detail="Item not found")

# Endpoint to create a new item
@app.post("/items/")
async def create_item(item: Item):
    item_document = item.dict()
    item_document["Item_id"] = str(uuid.uuid4())
    items_collection.insert_one(item_document)
    return {"message": "Item created successfully", "Item_id": item_document["Item_id"]}

# Endpoint to update an item by ID
@app.put("/items/{item_id}")
async def update_item(item_id: str, item: Item):
    update_result = items_collection.update_one({"_id": ObjectId(item_id)}, {"$set": item.dict()})
    if update_result.matched_count == 1:
        return {"message": "Item updated successfully"}
    raise HTTPException(status_code=404, detail="Item not found")

# Endpoint to delete an item by ID
@app.delete("/items/{item_id}")
async def delete_item(item_id: str):
    delete_result = items_collection.delete_one({"_id": ObjectId(item_id)})
    if delete_result.deleted_count == 1:
        return {"message": "Item deleted successfully"}
    raise HTTPException(status_code=404, detail="Item not found")

# Endpoint to generate a grocery list based on user preferences
@app.post("/generate_grocery_list/")
async def generate_grocery_list_endpoint(user_id: str):
    user = users_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Prepare user preferences to pass to the OpenAI function
    user_preferences = {
        "Budget": user["Budget"],
        "Dietary_restrictions": user["Dietary_restrictions"],
        "Allergies": user["Allergies"],
        "Food_request": user["Food_request"],
        "Preferred_stores": user["Preferred_stores"]
    }

    # Generate grocery list using the OpenAI API
    grocery_list = generate_grocery_list(user_preferences)
    
    return {"grocery_list": grocery_list}
