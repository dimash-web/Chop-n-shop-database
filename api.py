from fastapi import FastAPI, HTTPException
from main import items_collection
from pydantic import BaseModel
from bson import ObjectId
import uuid

app = FastAPI()

# run 'uvicorn api:app --reload' to test 

class Item(BaseModel):
    Item_name: str
    Store_name: str
    Price: float
    Ingredients: list[str]
    Calories: int

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Chop-n-Shop API!"}


#get (view) all items 
@app.get("/items/")
async def get_items():
    items = list(items_collection.find({}, {"_id": 0}))
    return items


#get (view) an item (by id)
@app.get("/items/{item_id}")
async def get_item(item_id: str):
    item = items_collection.find_one({"Item_id": item_id})
    if item:
        item["_id"] = str(item["_id"])  
        return item
    raise HTTPException(status_code=404, detail="Item not found")


#post (create) a new item
@app.post("/items/")
async def create_item(item: Item):
    item_document = item.dict()
    item_document["Item_id"] = str(uuid.uuid4())
    items_collection.insert_one(item_document)
    return {"message": "Item created successfully", "Item_id": item_document["Item_id"]}

#put (update) an item
@app.put("/items/{item_id}")
async def update_item(item_id: str, item: Item):
    update_result = items_collection.update_one({"_id": ObjectId(item_id)}, {"$set": item.dict()})
    if update_result.matched_count == 1:
        return {"message": "Item updated successfully"}
    raise HTTPException(status_code=404, detail="Item not found")

#delete an item
@app.delete("/items/{item_id}")
async def delete_item(item_id: str):
    delete_result = items_collection.delete_one({"_id": ObjectId(item_id)})
    if delete_result.deleted_count == 1:
        return {"message": "Item deleted successfully"}
    raise HTTPException(status_code=404, detail="Item not found")