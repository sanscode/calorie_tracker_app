from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from backend.models.diet_plan import DietPlan, Meal, PyObjectId
from backend.models.food_item import FoodItem
from backend.main import db
from backend.auth.auth import get_current_user
from bson import ObjectId

router = APIRouter(
    prefix="/diet-plans",
    tags=["diet-plans"]
)

@router.post("/", response_model=DietPlan, status_code=status.HTTP_201_CREATED)
async def create_diet_plan(diet_plan: DietPlan, current_user: str = Depends(get_current_user)):
    if not await validate_diet_plan(diet_plan):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid diet plan data")
    
    diet_plan.user_id = ObjectId(current_user.id)
    diet_plan_dict = diet_plan.dict(by_alias=True, exclude_unset=True)
    result = db.diet_plans.insert_one(diet_plan_dict)
    diet_plan.id = result.inserted_id
    return diet_plan

@router.get("/", response_model=List[DietPlan])
async def get_all_diet_plans(current_user: str = Depends(get_current_user)):
    diet_plans = []
    for plan in db.diet_plans.find({"user_id": ObjectId(current_user.id)}):
        diet_plans.append(DietPlan(**plan))
    return diet_plans

@router.get("/{id}", response_model=DietPlan)
async def get_diet_plan_by_id(id: str, current_user: str = Depends(get_current_user)):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Diet Plan ID")
    
    diet_plan = db.diet_plans.find_one({"_id": ObjectId(id), "user_id": ObjectId(current_user.id)})
    if diet_plan:
        return DietPlan(**diet_plan)
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Diet Plan not found")

@router.put("/{id}", response_model=DietPlan)
async def update_diet_plan(id: str, diet_plan: DietPlan, current_user: str = Depends(get_current_user)):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Diet Plan ID")
    
    if not await validate_diet_plan(diet_plan):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid diet plan data")

    diet_plan.user_id = ObjectId(current_user.id) # Ensure user_id is not changed by client
    diet_plan_dict = diet_plan.dict(by_alias=True, exclude_unset=True)
    updated_plan = db.diet_plans.find_one_and_update(
        {"_id": ObjectId(id), "user_id": ObjectId(current_user.id)},
        {"$set": diet_plan_dict},
        return_document=True
    )
    if updated_plan:
        return DietPlan(**updated_plan)
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Diet Plan not found")

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_diet_plan(id: str, current_user: str = Depends(get_current_user)):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Diet Plan ID")
    
    delete_result = db.diet_plans.delete_one({"_id": ObjectId(id), "user_id": ObjectId(current_user.id)})
    if delete_result.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Diet Plan not found")
    return {"message": "Diet Plan deleted successfully"}