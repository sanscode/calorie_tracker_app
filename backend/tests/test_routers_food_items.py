import pytest
from fastapi.testclient import TestClient
from backend.models.user import User
from backend.models.food_item import FoodItem
from backend.schemas.food_item import FoodItemCreate, FoodItemUpdate


class TestFoodItemsRouter:
    """Test cases for the food items router."""
    
    def test_create_food_item_success(self, client, db_session, sample_user):
        """Test successful food item creation."""
        # Login to get token
        login_response = client.post("/auth/login", data={
            "username": sample_user.username,
            "password": "testpassword"
        })
        token = login_response.json()["access_token"]
        
        food_item_data = {
            "name": "Apple",
            "calories": 52,
            "protein": 0.3,
            "carbs": 14,
            "fat": 0.2
        }
        
        headers = {"Authorization": f"Bearer {token}"}
        response = client.post("/food-items/", json=food_item_data, headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Apple"
        assert data["calories"] == 52
        assert data["protein"] == 0.3
        assert data["carbs"] == 14
        assert data["fat"] == 0.2
        assert data["user_id"] == sample_user.id
    
    def test_create_food_item_global(self, client, db_session):
        """Test creating a global food item (without authentication)."""
        food_item_data = {
            "name": "Banana",
            "calories": 89,
            "protein": 1.1,
            "carbs": 23,
            "fat": 0.3
        }
        
        response = client.post("/food-items/", json=food_item_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Banana"
        assert data["calories"] == 89
        assert data["protein"] == 1.1
        assert data["carbs"] == 23
        assert data["fat"] == 0.3
        assert data["user_id"] is None
    
    def test_create_food_item_missing_name(self, client, db_session, sample_user):
        """Test creating food item without name."""
        # Login to get token
        login_response = client.post("/auth/login", data={
            "username": sample_user.username,
            "password": "testpassword"
        })
        token = login_response.json()["access_token"]
        
        food_item_data = {
            "calories": 52,
            "protein": 0.3,
            "carbs": 14,
            "fat": 0.2
        }
        
        headers = {"Authorization": f"Bearer {token}"}
        response = client.post("/food-items/", json=food_item_data, headers=headers)
        
        assert response.status_code == 422  # Validation error
    
    def test_get_food_item_by_id(self, client, db_session, sample_food_item):
        """Test getting food item by ID."""
        response = client.get(f"/food-items/{sample_food_item.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_food_item.id
        assert data["name"] == sample_food_item.name
        assert data["calories"] == sample_food_item.calories
        assert data["protein"] == sample_food_item.protein
        assert data["carbs"] == sample_food_item.carbs
        assert data["fat"] == sample_food_item.fat
        assert data["user_id"] == sample_food_item.user_id
    
    def test_get_food_item_by_id_not_found(self, client, db_session):
        """Test getting food item by ID that doesn't exist."""
        response = client.get("/food-items/99999")
        
        assert response.status_code == 404
        assert "Food item not found" in response.json()["detail"]
    
    def test_get_food_items_global(self, client, db_session):
        """Test getting all global food items."""
        # Create some global food items
        food_item1 = FoodItem(name="Apple", calories=52, protein=0.3, carbs=14, fat=0.2)
        food_item2 = FoodItem(name="Banana", calories=89, protein=1.1, carbs=23, fat=0.3)
        db_session.add_all([food_item1, food_item2])
        db_session.commit()
        
        response = client.get("/food-items/")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert any(item["name"] == "Apple" for item in data)
        assert any(item["name"] == "Banana" for item in data)
    
    def test_get_food_items_by_user(self, client, db_session, sample_user):
        """Test getting food items for a specific user."""
        # Login to get token
        login_response = client.post("/auth/login", data={
            "username": sample_user.username,
            "password": "testpassword"
        })
        token = login_response.json()["access_token"]
        
        # Create food items for the user
        food_item1 = FoodItem(name="User Apple", calories=52, protein=0.3, carbs=14, fat=0.2, user_id=sample_user.id)
        food_item2 = FoodItem(name="User Banana", calories=89, protein=1.1, carbs=23, fat=0.3, user_id=sample_user.id)
        db_session.add_all([food_item1, food_item2])
        db_session.commit()
        
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/food-items/user", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert any(item["name"] == "User Apple" for item in data)
        assert any(item["name"] == "User Banana" for item in data)
    
    def test_get_food_items_by_user_no_items(self, client, db_session, sample_user):
        """Test getting food items for user with no items."""
        # Login to get token
        login_response = client.post("/auth/login", data={
            "username": sample_user.username,
            "password": "testpassword"
        })
        token = login_response.json()["access_token"]
        
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/food-items/user", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0
    
    def test_get_food_items_by_user_not_authenticated(self, client, db_session):
        """Test getting food items for user without authentication."""
        response = client.get("/food-items/user")
        
        assert response.status_code == 401
        assert "Not authenticated" in response.json()["detail"]
    
    def test_update_food_item_success(self, client, db_session, sample_user, sample_food_item):
        """Test successful food item update."""
        # Login to get token
        login_response = client.post("/auth/login", data={
            "username": sample_user.username,
            "password": "testpassword"
        })
        token = login_response.json()["access_token"]
        
        update_data = {
            "name": "Updated Apple",
            "calories": 60,
            "protein": 0.5,
            "carbs": 15,
            "fat": 0.3
        }
        
        headers = {"Authorization": f"Bearer {token}"}
        response = client.put(f"/food-items/{sample_food_item.id}", json=update_data, headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Apple"
        assert data["calories"] == 60
        assert data["protein"] == 0.5
        assert data["carbs"] == 15
        assert data["fat"] == 0.3
        assert data["user_id"] == sample_food_item.user_id
    
    def test_update_food_item_partial(self, client, db_session, sample_user, sample_food_item):
        """Test partial food item update."""
        # Login to get token
        login_response = client.post("/auth/login", data={
            "username": sample_user.username,
            "password": "testpassword"
        })
        token = login_response.json()["access_token"]
        
        update_data = {
            "name": "Partially Updated Apple"
        }
        
        headers = {"Authorization": f"Bearer {token}"}
        response = client.put(f"/food-items/{sample_food_item.id}", json=update_data, headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Partially Updated Apple"
        assert data["calories"] == sample_food_item.calories  # Unchanged
        assert data["protein"] == sample_food_item.protein  # Unchanged
        assert data["carbs"] == sample_food_item.carbs  # Unchanged
        assert data["fat"] == sample_food_item.fat  # Unchanged
    
    def test_update_food_item_not_found(self, client, db_session, sample_user):
        """Test updating food item that doesn't exist."""
        # Login to get token
        login_response = client.post("/auth/login", data={
            "username": sample_user.username,
            "password": "testpassword"
        })
        token = login_response.json()["access_token"]
        
        update_data = {
            "name": "Nonexistent"
        }
        
        headers = {"Authorization": f"Bearer {token}"}
        response = client.put("/food-items/99999", json=update_data, headers=headers)
        
        assert response.status_code == 404
        assert "Food item not found" in response.json()["detail"]
    
    def test_update_food_item_not_owner(self, client, db_session, sample_user):
        """Test updating food item that doesn't belong to the user."""
        # Create another user
        other_user = User(
            username="otheruser",
            email="other@example.com",
            hashed_password="hashed_password"
        )
        db_session.add(other_user)
        db_session.commit()
        
        # Create food item for other user
        food_item = FoodItem(
            name="Other User's Apple",
            calories=52,
            protein=0.3,
            carbs=14,
            fat=0.2,
            user_id=other_user.id
        )
        db_session.add(food_item)
        db_session.commit()
        
        # Login as original user
        login_response = client.post("/auth/login", data={
            "username": sample_user.username,
            "password": "testpassword"
        })
        token = login_response.json()["access_token"]
        
        update_data = {
            "name": "Stolen Apple"
        }
        
        headers = {"Authorization": f"Bearer {token}"}
        response = client.put(f"/food-items/{food_item.id}", json=update_data, headers=headers)
        
        assert response.status_code == 403
        assert "Not authorized to update this food item" in response.json()["detail"]
    
    def test_delete_food_item_success(self, client, db_session, sample_user, sample_food_item):
        """Test successful food item deletion."""
        # Login to get token
        login_response = client.post("/auth/login", data={
            "username": sample_user.username,
            "password": "testpassword"
        })
        token = login_response.json()["access_token"]
        
        headers = {"Authorization": f"Bearer {token}"}
        response = client.delete(f"/food-items/{sample_food_item.id}", headers=headers)
        
        assert response.status_code == 200
        assert response.json()["message"] == "Food item deleted successfully"
        
        # Verify deletion
        response = client.get(f"/food-items/{sample_food_item.id}")
        assert response.status_code == 404
    
    def test_delete_food_item_not_found(self, client, db_session, sample_user):
        """Test deleting food item that doesn't exist."""
        # Login to get token
        login_response = client.post("/auth/login", data={
            "username": sample_user.username,
            "password": "testpassword"
        })
        token = login_response.json()["access_token"]
        
        headers = {"Authorization": f"Bearer {token}"}
        response = client.delete("/food-items/99999", headers=headers)
        
        assert response.status_code == 404
        assert "Food item not found" in response.json()["detail"]
    
    def test_delete_food_item_not_owner(self, client, db_session, sample_user):
        """Test deleting food item that doesn't belong to the user."""
        # Create another user
        other_user = User(
            username="otheruser",
            email="other@example.com",
            hashed_password="hashed_password"
        )
        db_session.add(other_user)
        db_session.commit()
        
        # Create food item for other user
        food_item = FoodItem(
            name="Other User's Apple",
            calories=52,
            protein=0.3,
            carbs=14,
            fat=0.2,
            user_id=other_user.id
        )
        db_session.add(food_item)
        db_session.commit()
        
        # Login as original user
        login_response = client.post("/auth/login", data={
            "username": sample_user.username,
            "password": "testpassword"
        })
        token = login_response.json()["access_token"]
        
        headers = {"Authorization": f"Bearer {token}"}
        response = client.delete(f"/food-items/{food_item.id}", headers=headers)
        
        assert response.status_code == 403
        assert "Not authorized to delete this food item" in response.json()["detail"]
    
    def test_create_food_item_with_user_id_in_data(self, client, db_session, sample_user):
        """Test that user_id in request data is ignored and set from token."""
        # Login to get token
        login_response = client.post("/auth/login", data={
            "username": sample_user.username,
            "password": "testpassword"
        })
        token = login_response.json()["access_token"]
        
        food_item_data = {
            "name": "Test Apple",
            "calories": 52,
            "protein": 0.3,
            "carbs": 14,
            "fat": 0.2,
            "user_id": 99999  # This should be ignored
        }
        
        headers = {"Authorization": f"Bearer {token}"}
        response = client.post("/food-items/", json=food_item_data, headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == sample_user.id  # Should be set from token, not from request