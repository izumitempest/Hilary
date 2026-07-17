from backend.models.user import User
from sqlmodel import select

def test_register_user(client):
    response = client.post(
        "/auth/register",
        json={"email": "test@example.com", "password": "password123", "full_name": "Test User"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["user"]["email"] == "test@example.com"

def test_login_user(client, session):
    # Register first
    client.post(
        "/auth/register",
        json={"email": "login@example.com", "password": "password123", "full_name": "Login User"}
    )
    
    # Manually verify user for test
    user = session.exec(select(User).where(User.email == "login@example.com")).first()
    user.is_verified = True
    session.commit()

    # Login
    response = client.post(
        "/auth/login",
        data={"username": "login@example.com", "password": "password123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_invalid_password(client, session):
    client.post(
        "/auth/register",
        json={"email": "wrong@example.com", "password": "password123", "full_name": "Wrong User"}
    )
    
    user = session.exec(select(User).where(User.email == "wrong@example.com")).first()
    user.is_verified = True
    session.commit()

    response = client.post(
        "/auth/login",
        data={"username": "wrong@example.com", "password": "wrongpassword"}
    )
    assert response.status_code == 401
