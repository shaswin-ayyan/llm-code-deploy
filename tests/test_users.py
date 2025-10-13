# Contents of the file: /my-fastapi-app/my-fastapi-app/tests/test_users.py

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_user():
    response = client.post("/api/v1/users/", json={"username": "testuser", "password": "testpass"})
    assert response.status_code == 201
    assert "id" in response.json()
    assert response.json()["username"] == "testuser"

def test_create_user_invalid_data():
    response = client.post("/api/v1/users/", json={"username": "", "password": "testpass"})
    assert response.status_code == 422  # Unprocessable Entity for invalid input

def test_get_user():
    response = client.get("/api/v1/users/1")  # Assuming user with ID 1 exists
    assert response.status_code == 200
    assert "username" in response.json()

def test_get_user_not_found():
    response = client.get("/api/v1/users/999")  # Assuming user with ID 999 does not exist
    assert response.status_code == 404  # Not Found for non-existing user