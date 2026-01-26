import pytest
from fastapi.testclient import TestClient
from backend.models.user import User
from backend.models.diet_plan import DietPlan
from backend.schemas.diet_plan import DietPlanCreate, DietPlanUpdate


class TestDietPlansRouter:
    """Test cases for the diet plans router."""
    
    def test_create_diet_plan_success(self, client, db_session, sample_user):
        """Test successful diet plan creation."""
        # Login to get token
        login_response = client.post("/auth/login", data={
            "username": sample_user.username,
            "password": "testpassword"
        })
        token = login_response.json()["access_token"]
        
        diet_plan_data = {
            "name": "Test Plan",
            "description": "A test diet plan",
            "target_calories": 2000,
            "target_protein": 150,
            "target_carbs": 250,
            "target_fat": 70
        }
        
        headers = {"Authorization": f"Bearer {token}"}
        response = client.post("/diet-plans/", json=diet_plan_data, headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == sample_user.id
        assert data["name"] == "Test Plan"
        assert data["description"] == "A test diet plan"
        assert data["target_calories"] == 2000
        assert data["target_protein"] == 150
        assert data["target_carbs"] == 250
        assert data["target_fat"] == 70
    
    def test_create_diet_plan_minimal_data(self, client, db_session, sample_user):
        """Test creating diet plan with minimal required data."""
        # Login to get token
        login_response = client.post("/auth/login", data={
            "username": sample_user.username,
            "password": "testpassword"
        })
        token = login_response.json()["access_token"]
        
        diet_plan_data = {
            "name": "Minimal Plan"
        }
        
        headers = {"Authorization": f"Bearer {token}"}
        response = client.post("/diet-plans/", json=diet_plan_data, headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == sample_user.id
        assert data["name"] == "Minimal Plan"
        assert data["description"] is None
        assert data["target_calories"] is None
        assert data["target_protein"] is None
        assert data["target_carbs"] is None
        assert data["target_fat"] is None
    
    def test_create_diet_plan_not_authenticated(self, client, db_session):
        """Test creating diet plan without authentication."""
        diet_plan_data = {
            "name": "Test Plan"
        }
        
        response = client.post("/diet-plans/", json=diet_plan_data)
        
        assert response.status_code == 401
        assert "Not authenticated" in response.json()["detail"]
    
    def test_get_diet_plan_by_id(self, client, db_session, sample_diet_plan):
        """Test getting diet plan by ID."""
        response = client.get(f"/diet-plans/{sample_diet_plan.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_diet_plan.id
        assert data["user_id"] == sample_diet_plan.user_id
        assert data["name"] == sample_diet_plan.name
        assert data["description"] == sample_diet_plan.description
        assert data["target_calories"] == sample_diet_plan.target_calories
        assert data["target_protein"] == sample_diet_plan.target_protein
        assert data["target_carbs"] == sample_diet_plan.target_carbs
        assert data["target_fat"] == sample_diet_plan.target_fat
    
    def test_get_diet_plan_by_id_not_found(self, client, db_session):
        """Test getting diet plan by ID that doesn't exist."""
        response = client.get("/diet-plans/99999")
        
        assert response.status_code == 404
        assert "Diet plan not found" in response.json()["detail"]
    
    def test_get_diet_plans_by_user(self, client, db_session, sample_user):
        """Test getting diet plans for a specific user."""
        # Login to get token
        login_response = client.post("/auth/login", data={
            "username": sample_user.username,
            "password": "testpassword"
        })
        token = login_response.json()["access_token"]
        
        # Create multiple diet plans for the user
        diet_plan1 = DietPlan(user_id=sample_user.id, name="Plan 1", description="First plan", target_calories=2000)
        diet_plan2 = DietPlan(user_id=sample_user.id, name="Plan 2", description="Second plan", target_calories=1800)
        db_session.add_all([diet_plan1, diet_plan2])
        db_session.commit()
        
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/diet-plans/user", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3  # Including the sample_diet_plan fixture
        assert any(plan["name"] == "Plan 1" for plan in data)
        assert any(plan["name"] == "Plan 2" for plan in data)
        assert any(plan["name"] == "Test Plan" for plan in data)
    
    def test_get_diet_plans_by_user_no_plans(self, client, db_session, sample_user):
        """Test getting diet plans for user with no plans."""
        # Login to get token
        login_response = client.post("/auth/login", data={
            "username": sample_user.username,
            "password": "testpassword"
        })
        token = login_response.json()["access_token"]
        
        # Remove the sample diet plan to test empty result
        db_session.delete(sample_user.diet_plans[0])
        db_session.commit()
        
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/diet-plans/user", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0
    
    def test_get_diet_plans_by_user_not_authenticated(self, client, db_session):
        """Test getting diet plans for user without authentication."""
        response = client.get("/diet-plans/user")
        
        assert response.status_code == 401
        assert "Not authenticated" in response.json()["detail"]
    
    def test_get_diet_plan_by_name(self, client, db_session, sample_user):
        """Test getting diet plan by name."""
        # Login to get token
        login_response = client.post("/auth/login", data={
            "username": sample_user.username,
            "password": "testpassword"
        })
        token = login_response.json()["access_token"]
        
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/diet-plans/name/Test Plan", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test Plan"
        assert data["user_id"] == sample_user.id
    
    def test_get_diet_plan_by_name_not_found(self, client, db_session, sample_user):
        """Test getting diet plan by name that doesn't exist."""
        # Login to get token
        login_response = client.post("/auth/login", data={
            "username": sample_user.username,
            "password": "testpassword"
        })
        token = login_response.json()["access_token"]
        
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/diet-plans/name/Nonexistent Plan", headers=headers)
        
        assert response.status_code == 404
        assert "Diet plan not found" in response.json()["detail"]
    
    def test_get_diet_plan_by_name_not_authenticated(self, client, db_session):
        """Test getting diet plan by name without authentication."""
        response = client.get("/diet-plans/name/Test Plan")
        
        assert response.status_code == 401
        assert "Not authenticated" in response.json()["detail"]
    
    def test_update_diet_plan_success(self, client, db_session, sample_user, sample_diet_plan):
        """Test successful diet plan update."""
        # Login to get token
        login_response = client.post("/auth/login", data={
            "username": sample_user.username,
            "password": "testpassword"
        })
        token = login_response.json()["access_token"]
        
        update_data = {
            "name": "Updated Plan",
            "description": "Updated description",
            "target_calories": 2500,
            "target_protein": 180,
            "target_carbs": 300,
            "target_fat": 80
        }
        
        headers = {"Authorization": f"Bearer {token}"}
        response = client.put(f"/diet-plans/{sample_diet_plan.id}", json=update_data, headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Plan"
        assert data["description"] == "Updated description"
        assert data["target_calories"] == 2500
        assert data["target_protein"] == 180
        assert data["target_carbs"] == 300
        assert data["target_fat"] == 80
        assert data["user_id"] == sample_user.id
    
    def test_update_diet_plan_partial(self, client, db_session, sample_user, sample_diet_plan):
        """Test partial diet plan update."""
        # Login to get token
        login_response = client.post("/auth/login", data={
            "username": sample_user.username,
            "password": "testpassword"
        })
        token = login_response.json()["access_token"]
        
        update_data = {
            "name": "Partially Updated Plan"
        }
        
        headers = {"Authorization": f"Bearer {token}"}
        response = client.put(f"/diet-plans/{sample_diet_plan.id}", json=update_data, headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Partially Updated Plan"
        assert data["description"] == sample_diet_plan.description  # Unchanged
        assert data["target_calories"] == sample_diet_plan.target_calories  # Unchanged
        assert data["target_protein"] == sample_diet_plan.target_protein  # Unchanged
        assert data["target_carbs"] == sample_diet_plan.target_carbs  # Unchanged
        assert data["target_fat"] == sample_diet_plan.target_fat  # Unchanged
    
    def test_update_diet_plan_not_found(self, client, db_session, sample_user):
        """Test updating diet plan that doesn't exist."""
        # Login to get token
        login_response = client.post("/auth/login", data={
            "username": sample_user.username,
            "password": "testpassword"
        })
        token = login_response.json()["access_token"]
        
        update_data = {
            "name": "Nonexistent Plan"
        }
        
        headers = {"Authorization": f"Bearer {token}"}
        response = client.put("/diet-plans/99999", json=update_data, headers=headers)
        
        assert response.status_code == 404
        assert "Diet plan not found" in response.json()["detail"]
    
    def test_update_diet_plan_not_owner(self, client, db_session, sample_user):
        """Test updating diet plan that doesn't belong to the user."""
        # Create another user
        other_user = User(
            username="otheruser",
            email="other@example.com",
            hashed_password="hashed_password"
        )
        db_session.add(other_user)
        db_session.commit()
        
        # Create diet plan for other user
        diet_plan = DietPlan(
            user_id=other_user.id,
            name="Other User's Plan",
            description="A plan for other user",
            target_calories=2000
        )
        db_session.add(diet_plan)
        db_session.commit()
        
        # Login as original user
        login_response = client.post("/auth/login", data={
            "username": sample_user.username,
            "password": "testpassword"
        })
        token = login_response.json()["access_token"]
        
        update_data = {
            "name": "Stolen Plan"
        }
        
        headers = {"Authorization": f"Bearer {token}"}
        response = client.put(f"/diet-plans/{diet_plan.id}", json=update_data, headers=headers)
        
        assert response.status_code == 403
        assert "Not authorized to update this diet plan" in response.json()["detail"]
    
    def test_delete_diet_plan_success(self, client, db_session, sample_user, sample_diet_plan):
        """Test successful diet plan deletion."""
        # Login to get token
        login_response = client.post("/auth/login", data={
            "username": sample_user.username,
            "password": "testpassword"
        })
        token = login_response.json()["access_token"]
        
        headers = {"Authorization": f"Bearer {token}"}
        response = client.delete(f"/diet-plans/{sample_diet_plan.id}", headers=headers)
        
        assert response.status_code == 200
        assert response.json()["message"] == "Diet plan deleted successfully"
        
        # Verify deletion
        response = client.get(f"/diet-plans/{sample_diet_plan.id}")
        assert response.status_code == 404
    
    def test_delete_diet_plan_not_found(self, client, db_session, sample_user):
        """Test deleting diet plan that doesn't exist."""
        # Login to get token
        login_response = client.post("/auth/login", data={
            "username": sample_user.username,
            "password": "testpassword"
        })
        token = login_response.json()["access_token"]
        
        headers = {"Authorization": f"Bearer {token}"}
        response = client.delete("/diet-plans/99999", headers=headers)
        
        assert response.status_code == 404
        assert "Diet plan not found" in response.json()["detail"]
    
    def test_delete_diet_plan_not_owner(self, client, db_session, sample_user):
        """Test deleting diet plan that doesn't belong to the user."""
        # Create another user
        other_user = User(
            username="otheruser",
            email="other@example.com",
            hashed_password="hashed_password"
        )
        db_session.add(other_user)
        db_session.commit()
        
        # Create diet plan for other user
        diet_plan = DietPlan(
            user_id=other_user.id,
            name="Other User's Plan",
            description="A plan for other user",
            target_calories=2000
        )
        db_session.add(diet_plan)
        db_session.commit()
        
        # Login as original user
        login_response = client.post("/auth/login", data={
            "username": sample_user.username,
            "password": "testpassword"
        })
        token = login_response.json()["access_token"]
        
        headers = {"Authorization": f"Bearer {token}"}
        response = client.delete(f"/diet-plans/{diet_plan.id}", headers=headers)
        
        assert response.status_code == 403
        assert "Not authorized to delete this diet plan" in response.json()["detail"]
    
    def test_get_diet_plans_by_user_different_user(self, client, db_session, sample_user):
        """Test that users can only see their own diet plans."""
        # Create another user
        other_user = User(
            username="otheruser",
            email="other@example.com",
            hashed_password="hashed_password"
        )
        db_session.add(other_user)
        db_session.commit()
        
        # Create diet plans for both users
        diet_plan1 = DietPlan(user_id=sample_user.id, name="User1 Plan", target_calories=2000)
        diet_plan2 = DietPlan(user_id=other_user.id, name="User2 Plan", target_calories=1800)
        db_session.add_all([diet_plan1, diet_plan2])
        db_session.commit()
        
        # Login as first user
        login_response = client.post("/auth/login", data={
            "username": sample_user.username,
            "password": "testpassword"
        })
        token = login_response.json()["access_token"]
        
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/diet-plans/user", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2  # Including the sample_diet_plan fixture
        assert any(plan["name"] == "User1 Plan" for plan in data)
        assert not any(plan["name"] == "User2 Plan" for plan in data)
        assert all(plan["user_id"] == sample_user.id for plan in data)
    
    def test_create_diet_plan_with_existing_name(self, client, db_session, sample_user):
        """Test creating diet plan with name that already exists for the user."""
        # Login to get token
        login_response = client.post("/auth/login", data={
            "username": sample_user.username,
            "password": "testpassword"
        })
        token = login_response.json()["access_token"]
        
        # Create another diet plan with the same name
        diet_plan_data = {
            "name": "Test Plan",  # Same name as sample_diet_plan
            "description": "Another plan with same name"
        }
        
        headers = {"Authorization": f"Bearer {token}"}
        response = client.post("/diet-plans/", json=diet_plan_data, headers=headers)
        
        # This should succeed as the database schema doesn't enforce unique names per user
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test Plan"
        assert data["user_id"] == sample_user.id