import pytest
from fastapi.testclient import TestClient
from backend.models.user import User
from backend.models.food_item import FoodItem
from backend.models.calorie_log import CalorieLog
from backend.schemas.calorie_log import CalorieLogCreate, CalorieLogUpdate


class TestCalorieLogsRouter:
    """Test cases for the calorie logs router."""
    
    def test_create_calorie_log_success(self, client, db_session, sample_user, sample_food_item):
        """Test successful calorie log creation."""
        # Login to get token
        login_response = client.post("/auth/login", data={
            "username": sample_user.username,
            "password": "testpassword"
        })
        token = login_response.json()["access_token"]
        
        calorie_log_data = {
            "food_item_id": sample_food_item.id,
            "quantity": 2,
            "date": "2024-01-01"
        }
        
        headers = {"Authorization": f"Bearer {token}"}
        response = client.post("/calorie-logs/", json=calorie_log_data, headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == sample_user.id
        assert data["food_item_id"] == sample_food_item.id
        assert data["quantity"] == 2
        assert data["date"] == "2024-01-01"
    
    def test_create_calorie_log_default_date(self, client, db_session, sample_user, sample_food_item):
        """Test creating calorie log with default date."""
        # Login to get token
        login_response = client.post("/auth/login", data={
            "username": sample_user.username,
            "password": "testpassword"
        })
        token = login_response.json()["access_token"]
        
        calorie_log_data = {
            "food_item_id": sample_food_item.id,
            "quantity": 1
        }
        
        headers = {"Authorization": f"Bearer {token}"}
        response = client.post("/calorie-logs/", json=calorie_log_data, headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == sample_user.id
        assert data["food_item_id"] == sample_food_item.id
        assert data["quantity"] == 1
        assert data["date"] is not None
    
    def test_create_calorie_log_food_item_not_found(self, client, db_session, sample_user):
        """Test creating calorie log with non-existent food item."""
        # Login to get token
        login_response = client.post("/auth/login", data={
            "username": sample_user.username,
            "password": "testpassword"
        })
        token = login_response.json()["access_token"]
        
        calorie_log_data = {
            "food_item_id": 99999,
            "quantity": 1
        }
        
        headers = {"Authorization": f"Bearer {token}"}
        response = client.post("/calorie-logs/", json=calorie_log_data, headers=headers)
        
        assert response.status_code == 404
        assert "Food item not found" in response.json()["detail"]
    
    def test_create_calorie_log_not_authenticated(self, client, db_session, sample_food_item):
        """Test creating calorie log without authentication."""
        calorie_log_data = {
            "food_item_id": sample_food_item.id,
            "quantity": 1
        }
        
        response = client.post("/calorie-logs/", json=calorie_log_data)
        
        assert response.status_code == 401
        assert "Not authenticated" in response.json()["detail"]
    
    def test_get_calorie_log_by_id(self, client, db_session, sample_calorie_log):
        """Test getting calorie log by ID."""
        response = client.get(f"/calorie-logs/{sample_calorie_log.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_calorie_log.id
        assert data["user_id"] == sample_calorie_log.user_id
        assert data["food_item_id"] == sample_calorie_log.food_item_id
        assert data["quantity"] == sample_calorie_log.quantity
        assert data["date"] == sample_calorie_log.date
    
    def test_get_calorie_log_by_id_not_found(self, client, db_session):
        """Test getting calorie log by ID that doesn't exist."""
        response = client.get("/calorie-logs/99999")
        
        assert response.status_code == 404
        assert "Calorie log not found" in response.json()["detail"]
    
    def test_get_calorie_logs_by_user(self, client, db_session, sample_user):
        """Test getting calorie logs for a specific user."""
        # Login to get token
        login_response = client.post("/auth/login", data={
            "username": sample_user.username,
            "password": "testpassword"
        })
        token = login_response.json()["access_token"]
        
        # Create multiple calorie logs for the user
        food_item1 = FoodItem(name="Apple", calories=52, user_id=sample_user.id)
        food_item2 = FoodItem(name="Banana", calories=89, user_id=sample_user.id)
        db_session.add_all([food_item1, food_item2])
        db_session.commit()
        
        calorie_log1 = CalorieLog(user_id=sample_user.id, food_item_id=food_item1.id, quantity=2, date="2024-01-01")
        calorie_log2 = CalorieLog(user_id=sample_user.id, food_item_id=food_item2.id, quantity=1, date="2024-01-02")
        db_session.add_all([calorie_log1, calorie_log2])
        db_session.commit()
        
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/calorie-logs/user", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert any(log["food_item_id"] == food_item1.id for log in data)
        assert any(log["food_item_id"] == food_item2.id for log in data)
    
    def test_get_calorie_logs_by_user_no_logs(self, client, db_session, sample_user):
        """Test getting calorie logs for user with no logs."""
        # Login to get token
        login_response = client.post("/auth/login", data={
            "username": sample_user.username,
            "password": "testpassword"
        })
        token = login_response.json()["access_token"]
        
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/calorie-logs/user", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0
    
    def test_get_calorie_logs_by_user_not_authenticated(self, client, db_session):
        """Test getting calorie logs for user without authentication."""
        response = client.get("/calorie-logs/user")
        
        assert response.status_code == 401
        assert "Not authenticated" in response.json()["detail"]
    
    def test_get_calorie_logs_by_date(self, client, db_session, sample_user):
        """Test getting calorie logs for a specific date."""
        # Login to get token
        login_response = client.post("/auth/login", data={
            "username": sample_user.username,
            "password": "testpassword"
        })
        token = login_response.json()["access_token"]
        
        # Create food items and calorie logs
        food_item1 = FoodItem(name="Apple", calories=52, user_id=sample_user.id)
        food_item2 = FoodItem(name="Banana", calories=89, user_id=sample_user.id)
        db_session.add_all([food_item1, food_item2])
        db_session.commit()
        
        calorie_log1 = CalorieLog(user_id=sample_user.id, food_item_id=food_item1.id, quantity=2, date="2024-01-01")
        calorie_log2 = CalorieLog(user_id=sample_user.id, food_item_id=food_item2.id, quantity=1, date="2024-01-01")
        calorie_log3 = CalorieLog(user_id=sample_user.id, food_item_id=food_item1.id, quantity=1, date="2024-01-02")
        db_session.add_all([calorie_log1, calorie_log2, calorie_log3])
        db_session.commit()
        
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/calorie-logs/date/2024-01-01", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert all(log["date"] == "2024-01-01" for log in data)
    
    def test_get_calorie_logs_by_date_no_logs(self, client, db_session, sample_user):
        """Test getting calorie logs for a date with no logs."""
        # Login to get token
        login_response = client.post("/auth/login", data={
            "username": sample_user.username,
            "password": "testpassword"
        })
        token = login_response.json()["access_token"]
        
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/calorie-logs/date/2024-01-01", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0
    
    def test_get_calorie_logs_by_date_not_authenticated(self, client, db_session):
        """Test getting calorie logs by date without authentication."""
        response = client.get("/calorie-logs/date/2024-01-01")
        
        assert response.status_code == 401
        assert "Not authenticated" in response.json()["detail"]
    
    def test_update_calorie_log_success(self, client, db_session, sample_user, sample_calorie_log):
        """Test successful calorie log update."""
        # Login to get token
        login_response = client.post("/auth/login", data={
            "username": sample_user.username,
            "password": "testpassword"
        })
        token = login_response.json()["access_token"]
        
        update_data = {
            "quantity": 3,
            "date": "2024-01-02"
        }
        
        headers = {"Authorization": f"Bearer {token}"}
        response = client.put(f"/calorie-logs/{sample_calorie_log.id}", json=update_data, headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["quantity"] == 3
        assert data["date"] == "2024-01-02"
        assert data["user_id"] == sample_calorie_log.user_id
        assert data["food_item_id"] == sample_calorie_log.food_item_id
    
    def test_update_calorie_log_partial(self, client, db_session, sample_user, sample_calorie_log):
        """Test partial calorie log update."""
        # Login to get token
        login_response = client.post("/auth/login", data={
            "username": sample_user.username,
            "password": "testpassword"
        })
        token = login_response.json()["access_token"]
        
        update_data = {
            "quantity": 5
        }
        
        headers = {"Authorization": f"Bearer {token}"}
        response = client.put(f"/calorie-logs/{sample_calorie_log.id}", json=update_data, headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["quantity"] == 5
        assert data["date"] == sample_calorie_log.date  # Unchanged
        assert data["user_id"] == sample_calorie_log.user_id
        assert data["food_item_id"] == sample_calorie_log.food_item_id
    
    def test_update_calorie_log_not_found(self, client, db_session, sample_user):
        """Test updating calorie log that doesn't exist."""
        # Login to get token
        login_response = client.post("/auth/login", data={
            "username": sample_user.username,
            "password": "testpassword"
        })
        token = login_response.json()["access_token"]
        
        update_data = {
            "quantity": 3
        }
        
        headers = {"Authorization": f"Bearer {token}"}
        response = client.put("/calorie-logs/99999", json=update_data, headers=headers)
        
        assert response.status_code == 404
        assert "Calorie log not found" in response.json()["detail"]
    
    def test_update_calorie_log_not_owner(self, client, db_session, sample_user):
        """Test updating calorie log that doesn't belong to the user."""
        # Create another user
        other_user = User(
            username="otheruser",
            email="other@example.com",
            hashed_password="hashed_password"
        )
        db_session.add(other_user)
        db_session.commit()
        
        # Create food item and calorie log for other user
        food_item = FoodItem(name="Apple", calories=52, user_id=other_user.id)
        db_session.add(food_item)
        db_session.commit()
        
        calorie_log = CalorieLog(user_id=other_user.id, food_item_id=food_item.id, quantity=2, date="2024-01-01")
        db_session.add(calorie_log)
        db_session.commit()
        
        # Login as original user
        login_response = client.post("/auth/login", data={
            "username": sample_user.username,
            "password": "testpassword"
        })
        token = login_response.json()["access_token"]
        
        update_data = {
            "quantity": 3
        }
        
        headers = {"Authorization": f"Bearer {token}"}
        response = client.put(f"/calorie-logs/{calorie_log.id}", json=update_data, headers=headers)
        
        assert response.status_code == 403
        assert "Not authorized to update this calorie log" in response.json()["detail"]
    
    def test_delete_calorie_log_success(self, client, db_session, sample_user, sample_calorie_log):
        """Test successful calorie log deletion."""
        # Login to get token
        login_response = client.post("/auth/login", data={
            "username": sample_user.username,
            "password": "testpassword"
        })
        token = login_response.json()["access_token"]
        
        headers = {"Authorization": f"Bearer {token}"}
        response = client.delete(f"/calorie-logs/{sample_calorie_log.id}", headers=headers)
        
        assert response.status_code == 200
        assert response.json()["message"] == "Calorie log deleted successfully"
        
        # Verify deletion
        response = client.get(f"/calorie-logs/{sample_calorie_log.id}")
        assert response.status_code == 404
    
    def test_delete_calorie_log_not_found(self, client, db_session, sample_user):
        """Test deleting calorie log that doesn't exist."""
        # Login to get token
        login_response = client.post("/auth/login", data={
            "username": sample_user.username,
            "password": "testpassword"
        })
        token = login_response.json()["access_token"]
        
        headers = {"Authorization": f"Bearer {token}"}
        response = client.delete("/calorie-logs/99999", headers=headers)
        
        assert response.status_code == 404
        assert "Calorie log not found" in response.json()["detail"]
    
    def test_delete_calorie_log_not_owner(self, client, db_session, sample_user):
        """Test deleting calorie log that doesn't belong to the user."""
        # Create another user
        other_user = User(
            username="otheruser",
            email="other@example.com",
            hashed_password="hashed_password"
        )
        db_session.add(other_user)
        db_session.commit()
        
        # Create food item and calorie log for other user
        food_item = FoodItem(name="Apple", calories=52, user_id=other_user.id)
        db_session.add(food_item)
        db_session.commit()
        
        calorie_log = CalorieLog(user_id=other_user.id, food_item_id=food_item.id, quantity=2, date="2024-01-01")
        db_session.add(calorie_log)
        db_session.commit()
        
        # Login as original user
        login_response = client.post("/auth/login", data={
            "username": sample_user.username,
            "password": "testpassword"
        })
        token = login_response.json()["access_token"]
        
        headers = {"Authorization": f"Bearer {token}"}
        response = client.delete(f"/calorie-logs/{calorie_log.id}", headers=headers)
        
        assert response.status_code == 403
        assert "Not authorized to delete this calorie log" in response.json()["detail"]
    
    def test_get_calorie_logs_by_user_different_user(self, client, db_session, sample_user):
        """Test that users can only see their own calorie logs."""
        # Create another user
        other_user = User(
            username="otheruser",
            email="other@example.com",
            hashed_password="hashed_password"
        )
        db_session.add(other_user)
        db_session.commit()
        
        # Create food items and calorie logs for both users
        food_item1 = FoodItem(name="User1 Apple", calories=52, user_id=sample_user.id)
        food_item2 = FoodItem(name="User2 Apple", calories=52, user_id=other_user.id)
        db_session.add_all([food_item1, food_item2])
        db_session.commit()
        
        calorie_log1 = CalorieLog(user_id=sample_user.id, food_item_id=food_item1.id, quantity=2, date="2024-01-01")
        calorie_log2 = CalorieLog(user_id=other_user.id, food_item_id=food_item2.id, quantity=1, date="2024-01-01")
        db_session.add_all([calorie_log1, calorie_log2])
        db_session.commit()
        
        # Login as first user
        login_response = client.post("/auth/login", data={
            "username": sample_user.username,
            "password": "testpassword"
        })
        token = login_response.json()["access_token"]
        
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/calorie-logs/user", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["food_item_id"] == food_item1.id
        assert data[0]["user_id"] == sample_user.id