from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
from pymongo import MongoClient
from routers import auth, food_items, diet_plans, calorie_logs
from models.user import User
from auth.auth import get_password_hash, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from datetime import timedelta

load_dotenv()

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client.healthyfoodapp

app.include_router(auth.router, tags=["auth"])
app.include_router(food_items.router, tags=["food-items"])
app.include_router(diet_plans.router, tags=["diet-plans"])
app.include_router(calorie_logs.router, tags=["calorie-logs"])

@app.post("/register", response_model=dict)
async def register_user(user: User):
    existing_user = db.users.find_one({"username": user.username})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    existing_email = db.users.find_one({"email": user.email})
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Hash the password before storing
    hashed_password = get_password_hash(user.hashed_password)
    
    # Create user dict and update the password
    user_dict = user.dict(by_alias=True, exclude_unset=True)
    user_dict["hashed_password"] = hashed_password
    
    db.users.insert_one(user_dict)

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"message": "User registered successfully", "access_token": access_token, "token_type": "bearer"}

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Healthy Food App Backend!"}