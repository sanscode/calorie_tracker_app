from typing import List
from backend.models.diet_plan import DietPlan, Meal
from backend.models.food_item import FoodItem
from backend.main import db
from bson import ObjectId

async def calculate_diet_plan_calories(diet_plan: DietPlan) -> float:
    total_calories = 0.0
    for meal in diet_plan.meals:
        food_item_data = db.food_items.find_one({"_id": ObjectId(meal.food_item_id)})
        if food_item_data:
            food_item = FoodItem(**food_item_data)
            total_calories += food_item.calories * meal.quantity
    return total_calories

async def validate_diet_plan(diet_plan: DietPlan) -> bool:
    # Example validation: Ensure all food items exist
    for meal in diet_plan.meals:
        food_item_data = db.food_items.find_one({"_id": ObjectId(meal.food_item_id)})
        if not food_item_data:
            return False # Food item not found
    
    # Add more complex validation logic here, e.g.,
    # - Check if total calories are within a healthy range for the user
    # - Check for balanced macros (protein, carbs, fat)
    # - Ensure quantities are positive

    return True