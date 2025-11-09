import json
import pytest
from run import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_register_success(client):
    # Register a new user
    response = client.post('/register', json={
        "username": "testuser",
        "password": "TestPass123",
        "groups": ["User"]
    })
    data = json.loads(response.data)
    assert response.status_code == 200
    assert data["success"] is True
    assert "user_id" in data

def test_register_missing_fields(client):
    response = client.post('/register', json={"username": "testuser"})
    assert response.status_code == 400

def test_login_success(client):
    # First register
    client.post('/register', json={
        "username": "loginuser",
        "password": "LoginPass123",
        "groups": ["User"]
    })
    # Then login
    response = client.post('/login', data={
        "username": "loginuser",
        "password": "LoginPass123"
    }, follow_redirects=False)
    # Should redirect to dashboard
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/dashboard")

def test_login_invalid_credentials(client):
    response = client.post('/login', data={
        "username": "nonexistent",
        "password": "wrong"
    }, follow_redirects=False)
    # Should redirect back to login page
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/")