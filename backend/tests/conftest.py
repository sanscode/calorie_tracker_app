import pytest
import asyncio
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
from main import db
from models.user import User
from models.food_item import FoodItem
from models.calorie_log import CalorieLog
from models.diet_plan import DietPlan
from sqlalchemy.ext.declarative import declarative_base

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[db] = override_get_db

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def client():
    """Create a test client."""
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db_session():
    """Create a database session for testing."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def sample_user(db_session):
    """Create a sample user for testing."""
    from auth.auth import get_password_hash
    
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=get_password_hash("testpassword"),
        full_name="Test User",
        age=25,
        weight=70.0,
        height=175.0,
        activity_level="moderate"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def sample_food_item(db_session, sample_user):
    """Create a sample food item for testing."""
    food_item = FoodItem(
        name="Apple",
        calories=52,
        protein=0.3,
        carbs=14,
        fat=0.2,
        user_id=sample_user.id
    )
    db_session.add(food_item)
    db_session.commit()
    db_session.refresh(food_item)
    return food_item

@pytest.fixture
def sample_calorie_log(db_session, sample_user, sample_food_item):
    """Create a sample calorie log for testing."""
    calorie_log = CalorieLog(
        user_id=sample_user.id,
        food_item_id=sample_food_item.id,
        quantity=2,
        date="2024-01-01"
    )
    db_session.add(calorie_log)
    db_session.commit()
    db_session.refresh(calorie_log)
    return calorie_log

@pytest.fixture
def sample_diet_plan(db_session, sample_user):
    """Create a sample diet plan for testing."""
    diet_plan = DietPlan(
        user_id=sample_user.id,
        name="Test Plan",
        description="A test diet plan",
        target_calories=2000,
        target_protein=150,
        target_carbs=250,
        target_fat=70
    )
    db_session.add(diet_plan)
    db_session.commit()
    db_session.refresh(diet_plan)
    return diet_plan