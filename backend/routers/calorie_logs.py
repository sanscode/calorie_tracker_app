from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from backend.models.calorie_log import CalorieLog, PyObjectId
from backend.models.food_item import FoodItem
from backend.main import db
from backend.auth.auth import get_current_user
from backend.services.diet_plan_service import calculate_diet_plan_calories # This import is not directly used here, but will be useful for future logic.
from bson import ObjectId
from datetime import date

router = APIRouter(
    prefix="/calorie-logs",
    tags=["calorie-logs"]
)

@router.post("/", response_model=CalorieLog, status_code=status.HTTP_201_CREATED)
async def create_calorie_log(calorie_log: CalorieLog, current_user: str = Depends(get_current_user)):
    calorie_log.user_id = ObjectId(current_user.id) # Assign the current user's ID
    
    # Fetch food item to calculate calories_consumed
    food_item = db.food_items.find_one({"_id": ObjectId(calorie_log.food_item_id)})
    if not food_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Food Item not found")
    
    food_item_obj = FoodItem(**food_item)
    calorie_log.calories_consumed = food_item_obj.calories * calorie_log.quantity

    calorie_log_dict = calorie_log.dict(by_alias=True, exclude_unset=True)
    result = db.calorie_logs.insert_one(calorie_log_dict)
    calorie_log.id = result.inserted_id
    return calorie_log

@router.get("/", response_model=List[CalorieLog])
async def get_all_calorie_logs(current_user: str = Depends(get_current_user)):
    calorie_logs = []
    for log in db.calorie_logs.find({"user_id": ObjectId(current_user.id)}):
        calorie_logs.append(CalorieLog(**log))
    return calorie_logs

@router.get("/daily/{log_date}", response_model=List[CalorieLog])
async def get_daily_calorie_logs(log_date: date, current_user: str = Depends(get_current_user)):
    calorie_logs = []
    for log in db.calorie_logs.find({"user_id": ObjectId(current_user.id), "log_date": log_date}):
        calorie_logs.append(CalorieLog(**log))
    return calorie_logs

@router.get("/{id}", response_model=CalorieLog)
async def get_calorie_log_by_id(id: str, current_user: str = Depends(get_current_user)):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Calorie Log ID")
    
    calorie_log = db.calorie_logs.find_one({"_id": ObjectId(id), "user_id": ObjectId(current_user.id)})
    if calorie_log:
        return CalorieLog(**calorie_log)
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Calorie Log not found")

@router.put("/{id}", response_model=CalorieLog)
async def update_calorie_log(id: str, calorie_log: CalorieLog, current_user: str = Depends(get_current_user)):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Calorie Log ID")
    
    # Recalculate calories_consumed if food_item_id or quantity changes
    food_item = db.food_items.find_one({"_id": ObjectId(calorie_log.food_item_id)})
    if not food_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Food Item not found")
    
    food_item_obj = FoodItem(**food_item)
    calorie_log.calories_consumed = food_item_obj.calories * calorie_log.quantity

    calorie_log_dict = calorie_log.dict(by_alias=True, exclude_unset=True)
    updated_log = db.calorie_logs.find_one_and_update(
        {"_id": ObjectId(id), "user_id": ObjectId(current_user.id)},
        {"$set": calorie_log_dict},
        return_document=True
    )
    if updated_log:
        return CalorieLog(**updated_log)
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Calorie Log not found")

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_calorie_log(id: str, current_user: str = Depends(get_current_user)):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Calorie Log ID")
    
    delete_result = db.calorie_logs.delete_one({"_id": ObjectId(id), "user_id": ObjectId(current_user.id)})
    if delete_result.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Calorie Log not found")
    return {"message": "Calorie Log deleted successfully"}