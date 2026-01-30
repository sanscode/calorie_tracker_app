#!/usr/bin/env python3
"""
Simple test script to verify the registration endpoint works
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
from models.user import User
from fastapi.testclient import TestClient

def test_registration():
    client = TestClient(app)
    
    # Test data
    test_user = {
        "username": "testuser7",
        "email": "test7@example.com", 
        "hashed_password": "testpassword127"  # This will be hashed by the endpoint
    }
    
    try:
        response = client.post("/register", json=test_user)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("✅ Registration endpoint works correctly!")
            return True
        else:
            print(f"❌ Registration failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing registration: {e}")
        return False

if __name__ == "__main__":
    test_registration()