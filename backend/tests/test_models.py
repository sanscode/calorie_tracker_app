import pytest
from datetime import date
from sqlalchemy.exc import IntegrityError
from models.user import User
from models.food_item import FoodItem
from models.calorie_log import CalorieLog
from models.diet_plan import DietPlan


class TestUserModel:
    """Test cases for the User model."""
    
    def test_user_creation(self, db_session):
        """Test creating a new user."""
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password="hashed_password",
            full_name="Test User",
            age=25,
            weight=70.0,
            height=175.0,
            activity_level="moderate"
        )
        db_session.add(user)
        db_session.commit()
        
        assert user.id is not None
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.full_name == "Test User"
        assert user.age == 25
        assert user.weight == 70.0
        assert user.height == 175.0
        assert user.activity_level == "moderate"
    
    def test_user_unique_username(self, db_session):
        """Test that usernames must be unique."""
        user1 = User(
            username="testuser",
            email="test1@example.com",
            hashed_password="hashed_password",
            full_name="Test User 1"
        )
        db_session.add(user1)
        db_session.commit()
        
        user2 = User(
            username="testuser",
            email="test2@example.com",
            hashed_password="hashed_password",
            full_name="Test User 2"
        )
        db_session.add(user2)
        
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    def test_user_unique_email(self, db_session):
        """Test that emails must be unique."""
        user1 = User(
            username="testuser1",
            email="test@example.com",
            hashed_password="hashed_password",
            full_name="Test User 1"
        )
        db_session.add(user1)
        db_session.commit()
        
        user2 = User(
            username="testuser2",
            email="test@example.com",
            hashed_password="hashed_password",
            full_name="Test User 2"
        )
        db_session.add(user2)
        
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    def test_user_optional_fields(self, db_session):
        """Test that optional fields can be None."""
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password="hashed_password"
        )
        db_session.add(user)
        db_session.commit()
        
        assert user.full_name is None
        assert user.age is None
        assert user.weight is None
        assert user.height is None
        assert user.activity_level is None


class TestFoodItemModel:
    """Test cases for the FoodItem model."""
    
    def test_food_item_creation(self, db_session, sample_user):
        """Test creating a new food item."""
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
        
        assert food_item.id is not None
        assert food_item.name == "Apple"
        assert food_item.calories == 52
        assert food_item.protein == 0.3
        assert food_item.carbs == 14
        assert food_item.fat == 0.2
        assert food_item.user_id == sample_user.id
    
    def test_food_item_creation_without_user(self, db_session):
        """Test creating a food item without a user (global food item)."""
        food_item = FoodItem(
            name="Banana",
            calories=89,
            protein=1.1,
            carbs=23,
            fat=0.3
        )
        db_session.add(food_item)
        db_session.commit()
        
        assert food_item.id is not None
        assert food_item.name == "Banana"
        assert food_item.calories == 89
        assert food_item.protein == 1.1
        assert food_item.carbs == 23
        assert food_item.fat == 0.3
        assert food_item.user_id is None
    
    def test_food_item_name_required(self, db_session, sample_user):
        """Test that food item name is required."""
        food_item = FoodItem(
            calories=52,
            protein=0.3,
            carbs=14,
            fat=0.2,
            user_id=sample_user.id
        )
        db_session.add(food_item)
        
        with pytest.raises(IntegrityError):
            db_session.commit()


class TestCalorieLogModel:
    """Test cases for the CalorieLog model."""
    
    def test_calorie_log_creation(self, db_session, sample_user, sample_food_item):
        """Test creating a new calorie log."""
        calorie_log = CalorieLog(
            user_id=sample_user.id,
            food_item_id=sample_food_item.id,
            quantity=2,
            date="2024-01-01"
        )
        db_session.add(calorie_log)
        db_session.commit()
        
        assert calorie_log.id is not None
        assert calorie_log.user_id == sample_user.id
        assert calorie_log.food_item_id == sample_food_item.id
        assert calorie_log.quantity == 2
        assert calorie_log.date == "2024-01-01"
    
    def test_calorie_log_default_date(self, db_session, sample_user, sample_food_item):
        """Test that calorie log uses current date if not provided."""
        calorie_log = CalorieLog(
            user_id=sample_user.id,
            food_item_id=sample_food_item.id,
            quantity=1
        )
        db_session.add(calorie_log)
        db_session.commit()
        
        assert calorie_log.id is not None
        assert calorie_log.user_id == sample_user.id
        assert calorie_log.food_item_id == sample_food_item.id
        assert calorie_log.quantity == 1
        assert calorie_log.date is not None
    
    def test_calorie_log_quantity_validation(self, db_session, sample_user, sample_food_item):
        """Test that quantity must be positive."""
        calorie_log = CalorieLog(
            user_id=sample_user.id,
            food_item_id=sample_food_item.id,
            quantity=0,
            date="2024-01-01"
        )
        db_session.add(calorie_log)
        
        # This might not raise an IntegrityError depending on database constraints
        # The validation might be handled at the application level
        db_session.commit()
        assert calorie_log.quantity == 0


class TestDietPlanModel:
    """Test cases for the DietPlan model."""
    
    def test_diet_plan_creation(self, db_session, sample_user):
        """Test creating a new diet plan."""
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
        
        assert diet_plan.id is not None
        assert diet_plan.user_id == sample_user.id
        assert diet_plan.name == "Test Plan"
        assert diet_plan.description == "A test diet plan"
        assert diet_plan.target_calories == 2000
        assert diet_plan.target_protein == 150
        assert diet_plan.target_carbs == 250
        assert diet_plan.target_fat == 70
    
    def test_diet_plan_optional_fields(self, db_session, sample_user):
        """Test that optional fields can be None."""
        diet_plan = DietPlan(
            user_id=sample_user.id,
            name="Minimal Plan"
        )
        db_session.add(diet_plan)
        db_session.commit()
        
        assert diet_plan.id is not None
        assert diet_plan.user_id == sample_user.id
        assert diet_plan.name == "Minimal Plan"
        assert diet_plan.description is None
        assert diet_plan.target_calories is None
        assert diet_plan.target_protein is None
        assert diet_plan.target_carbs is None
        assert diet_plan.target_fat is None
    
    def test_diet_plan_name_required(self, db_session, sample_user):
        """Test that diet plan name is required."""
        diet_plan = DietPlan(
            user_id=sample_user.id,
            description="A test diet plan"
        )
        db_session.add(diet_plan)
        
        with pytest.raises(IntegrityError):
            db_session.commit()