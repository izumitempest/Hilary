# pyrefly: ignore [missing-import]
import pytest
# pyrefly: ignore [missing-import]
from sqlmodel import select
from fastapi.testclient import TestClient
from backend.main import app
from backend.database import SQLModel, engine
from backend.models.user import User

client = TestClient(app)

def test_full_therapy_cycle(client, session):
    # 1. Register User
    client.post("/auth/register", json={"email": "live@example.com", "password": "password123", "full_name": "Live User"})
    
    # Manually verify user
    user = session.exec(select(User).where(User.email == "live@example.com")).first()
    user.is_verified = True
    session.commit()

    # 2. Login
    login_resp = client.post("/auth/login", data={"username": "live@example.com", "password": "password123"})
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print(f"Login: {login_resp.status_code}")
    
    # 3. Log "Anxious" Behavior (High screen time + high unlocks)
    behavior_resp = client.post("/behavior/log", headers=headers, json={
        "screen_time_seconds": 30000, # > 8 hours
        "unlock_count": 150,
        "app_usage": {"instagram": 15000, "docs": 2000}
    })
    print(f"Log Behavior: {behavior_resp.status_code}")
    
    # 4. Chat with Hilary
    print("Sending message: 'I feel really overwhelmed today...'")
    chat_resp = client.post("/chat/", headers=headers, json={
        "messages": [
            {"role": "user", "content": "I feel really overwhelmed today. I can't seem to focus on anything."}
        ],
        "text_sentiment": -0.6
    })
    
    assert chat_resp.status_code == 200, f"Chat failed: {chat_resp.text}"
    
    data = chat_resp.json()
    print(f"\nDetected Emotional State: {data['emotional_state']}")
    print(f"Hilary's Response:\n{data['response']}")
    
    assert "response" in data
    assert "emotional_state" in data
    assert data["emotional_state"] == "Critical Distress" # Based on behavior logged earlier + text sentiment -0.6
    
    # 5. Verify History Persistence
    print("Verifying history...")
    history_resp = client.get("/chat/history", headers=headers)
    assert history_resp.status_code == 200
    history = history_resp.json()
    assert len(history) >= 2
    assert history[-2]["role"] == "user"
    assert history[-1]["role"] == "assistant"
    print(f"History verified! Count: {len(history)}")

if __name__ == "__main__":
    test_full_system_flow()
