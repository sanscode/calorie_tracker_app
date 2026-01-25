from pydantic import BaseModel, Field
from typing import List, Optional
from bson import ObjectId
from datetime import date

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema: dict):
        field_schema.update(type="string")

class Meal(BaseModel):
    food_item_id: PyObjectId
    quantity: float # e.g., grams, number of servings

class DietPlan(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id")
    user_id: PyObjectId
    name: str
    target_calories: float
    meals: List[Meal] = []
    created_at: date = Field(default_factory=date.today)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str, date: lambda v: v.isoformat()}