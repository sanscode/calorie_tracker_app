from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from backend.models.food_item import FoodItem, PyObjectId
from backend.main import db
from backend.auth.auth import get_current_user
from bson import ObjectId

router = APIRouter(
    prefix="/food-items",
    tags=["food-items"]
)

@router.post("/", response_model=FoodItem, status_code=status.HTTP_201_CREATED)
async def create_food_item(food_item: FoodItem, current_user: str = Depends(get_current_user)):
    # For simplicity, assuming any logged-in user can create food items.
    # In a real app, you might add role-based access control here.
    food_item_dict = food_item.dict(by_alias=True, exclude_unset=True)
    result = db.food_items.insert_one(food_item_dict)
    food_item.id = result.inserted_id
    return food_item

@router.get("/", response_model=List[FoodItem])
async def get_all_food_items(current_user: str = Depends(get_current_user)):
    food_items = []
    for item in db.food_items.find():
        food_items.append(FoodItem(**item))
    return food_items

@router.get("/{id}", response_model=FoodItem)
async def get_food_item_by_id(id: str, current_user: str = Depends(get_current_user)):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Food Item ID")
    food_item = db.food_items.find_one({"_id": ObjectId(id)})
    if food_item:
        return FoodItem(**food_item)
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Food Item not found")

@router.put("/{id}", response_model=FoodItem)
async def update_food_item(id: str, food_item: FoodItem, current_user: str = Depends(get_current_user)):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Food Item ID")
    
    food_item_dict = food_item.dict(by_alias=True, exclude_unset=True)
    updated_item = db.food_items.find_one_and_update(
        {"_id": ObjectId(id)},
        {"$set": food_item_dict},
        return_document=True
    )
    if updated_item:
        return FoodItem(**updated_item)
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Food Item not found")

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_food_item(id: str, current_user: str = Depends(get_current_user)):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Food Item ID")
    
    delete_result = db.food_items.delete_one({"_id": ObjectId(id)})
    if delete_result.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Food Item not found")
    return {"message": "Food Item deleted successfully"}