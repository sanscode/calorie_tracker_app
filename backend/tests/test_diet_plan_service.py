import pytest
from sqlalchemy.orm import Session
from backend.services.diet_plan_service import DietPlanService
from backend.models.diet_plan import DietPlan
from backend.models.user import User
from backend.schemas.diet_plan import DietPlanCreate, DietPlanUpdate


class TestDietPlanService:
    """Test cases for the DietPlanService."""
    
    def test_create_diet_plan(self, db_session, sample_user):
        """Test creating a new diet plan."""
        service = DietPlanService(db_session)
        
        diet_plan_data = DietPlanCreate(
            name="Test Plan",
            description="A test diet plan",
            target_calories=2000,
            target_protein=150,
            target_carbs=250,
            target_fat=70
        )
        
        result = service.create_diet_plan(sample_user.id, diet_plan_data)
        
        assert result is not None
        assert result.name == "Test Plan"
        assert result.description == "A test diet plan"
        assert result.target_calories == 2000
        assert result.target_protein == 150
        assert result.target_carbs == 250
        assert result.target_fat == 70
        assert result.user_id == sample_user.id
    
    def test_get_diet_plan_by_id(self, db_session, sample_user, sample_diet_plan):
        """Test getting a diet plan by ID."""
        service = DietPlanService(db_session)
        
        result = service.get_diet_plan_by_id(sample_diet_plan.id)
        
        assert result is not None
        assert result.id == sample_diet_plan.id
        assert result.name == sample_diet_plan.name
        assert result.description == sample_diet_plan.description
        assert result.target_calories == sample_diet_plan.target_calories
        assert result.target_protein == sample_diet_plan.target_protein
        assert result.target_carbs == sample_diet_plan.target_carbs
        assert result.target_fat == sample_diet_plan.target_fat
        assert result.user_id == sample_diet_plan.user_id
    
    def test_get_diet_plan_by_id_not_found(self, db_session):
        """Test getting a diet plan by ID that doesn't exist."""
        service = DietPlanService(db_session)
        
        result = service.get_diet_plan_by_id(99999)
        
        assert result is None
    
    def test_get_diet_plans_by_user(self, db_session, sample_user):
        """Test getting all diet plans for a user."""
        service = DietPlanService(db_session)
        
        # Create multiple diet plans for the user
        diet_plan1 = DietPlan(
            user_id=sample_user.id,
            name="Plan 1",
            description="First plan",
            target_calories=2000
        )
        diet_plan2 = DietPlan(
            user_id=sample_user.id,
            name="Plan 2",
            description="Second plan",
            target_calories=1800
        )
        db_session.add_all([diet_plan1, diet_plan2])
        db_session.commit()
        
        result = service.get_diet_plans_by_user(sample_user.id)
        
        assert len(result) == 2
        assert any(plan.name == "Plan 1" for plan in result)
        assert any(plan.name == "Plan 2" for plan in result)
    
    def test_get_diet_plans_by_user_empty(self, db_session, sample_user):
        """Test getting diet plans for a user with no plans."""
        service = DietPlanService(db_session)
        
        result = service.get_diet_plans_by_user(sample_user.id)
        
        assert len(result) == 0
    
    def test_update_diet_plan(self, db_session, sample_user, sample_diet_plan):
        """Test updating a diet plan."""
        service = DietPlanService(db_session)
        
        update_data = DietPlanUpdate(
            name="Updated Plan",
            description="Updated description",
            target_calories=2500,
            target_protein=180,
            target_carbs=300,
            target_fat=80
        )
        
        result = service.update_diet_plan(sample_diet_plan.id, update_data)
        
        assert result is not None
        assert result.id == sample_diet_plan.id
        assert result.name == "Updated Plan"
        assert result.description == "Updated description"
        assert result.target_calories == 2500
        assert result.target_protein == 180
        assert result.target_carbs == 300
        assert result.target_fat == 80
        assert result.user_id == sample_user.id
    
    def test_update_diet_plan_partial(self, db_session, sample_user, sample_diet_plan):
        """Test updating only some fields of a diet plan."""
        service = DietPlanService(db_session)
        
        update_data = DietPlanUpdate(
            name="Updated Name Only"
        )
        
        result = service.update_diet_plan(sample_diet_plan.id, update_data)
        
        assert result is not None
        assert result.id == sample_diet_plan.id
        assert result.name == "Updated Name Only"
        assert result.description == sample_diet_plan.description  # Unchanged
        assert result.target_calories == sample_diet_plan.target_calories  # Unchanged
        assert result.target_protein == sample_diet_plan.target_protein  # Unchanged
        assert result.target_carbs == sample_diet_plan.target_carbs  # Unchanged
        assert result.target_fat == sample_diet_plan.target_fat  # Unchanged
        assert result.user_id == sample_user.id
    
    def test_update_diet_plan_not_found(self, db_session):
        """Test updating a diet plan that doesn't exist."""
        service = DietPlanService(db_session)
        
        update_data = DietPlanUpdate(name="Nonexistent Plan")
        
        result = service.update_diet_plan(99999, update_data)
        
        assert result is None
    
    def test_delete_diet_plan(self, db_session, sample_user, sample_diet_plan):
        """Test deleting a diet plan."""
        service = DietPlanService(db_session)
        
        result = service.delete_diet_plan(sample_diet_plan.id)
        
        assert result is True
        
        # Verify the plan was actually deleted
        deleted_plan = service.get_diet_plan_by_id(sample_diet_plan.id)
        assert deleted_plan is None
    
    def test_delete_diet_plan_not_found(self, db_session):
        """Test deleting a diet plan that doesn't exist."""
        service = DietPlanService(db_session)
        
        result = service.delete_diet_plan(99999)
        
        assert result is False
    
    def test_get_diet_plan_by_name(self, db_session, sample_user):
        """Test getting a diet plan by name."""
        service = DietPlanService(db_session)
        
        # Create a diet plan
        diet_plan = DietPlan(
            user_id=sample_user.id,
            name="Specific Plan",
            description="A specific plan",
            target_calories=2000
        )
        db_session.add(diet_plan)
        db_session.commit()
        
        result = service.get_diet_plan_by_name(sample_user.id, "Specific Plan")
        
        assert result is not None
        assert result.name == "Specific Plan"
        assert result.user_id == sample_user.id
    
    def test_get_diet_plan_by_name_not_found(self, db_session, sample_user):
        """Test getting a diet plan by name that doesn't exist."""
        service = DietPlanService(db_session)
        
        result = service.get_diet_plan_by_name(sample_user.id, "Nonexistent Plan")
        
        assert result is None
    
    def test_get_diet_plan_by_name_different_user(self, db_session, sample_user):
        """Test that getting a diet plan by name only returns plans for the specified user."""
        # Create another user
        other_user = User(
            username="otheruser",
            email="other@example.com",
            hashed_password="hashed_password"
        )
        db_session.add(other_user)
        db_session.commit()
        
        # Create diet plans for both users with the same name
        diet_plan1 = DietPlan(
            user_id=sample_user.id,
            name="Shared Name",
            target_calories=2000
        )
        diet_plan2 = DietPlan(
            user_id=other_user.id,
            name="Shared Name",
            target_calories=1800
        )
        db_session.add_all([diet_plan1, diet_plan2])
        db_session.commit()
        
        service = DietPlanService(db_session)
        
        # Should only return the plan for the specified user
        result = service.get_diet_plan_by_name(sample_user.id, "Shared Name")
        
        assert result is not None
        assert result.name == "Shared Name"
        assert result.user_id == sample_user.id
        assert result.target_calories == 2000
    
    def test_create_diet_plan_with_minimal_data(self, db_session, sample_user):
        """Test creating a diet plan with only required fields."""
        service = DietPlanService(db_session)
        
        diet_plan_data = DietPlanCreate(name="Minimal Plan")
        
        result = service.create_diet_plan(sample_user.id, diet_plan_data)
        
        assert result is not None
        assert result.name == "Minimal Plan"
        assert result.description is None
        assert result.target_calories is None
        assert result.target_protein is None
        assert result.target_carbs is None
        assert result.target_fat is None
        assert result.user_id == sample_user.id