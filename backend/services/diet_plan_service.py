from typing import List
from models.diet_plan import DietPlan, Meal
from models.food_item import FoodItem
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client.healthyfoodapp
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