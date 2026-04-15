import time
from fastapi.testclient import TestClient
from backend.main import app
from backend.database import SQLModel, engine

client = TestClient(app)

def test_full_system_flow():
    # 0. Clean DB for test
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
    
    print("\n--- Starting Live system Test ---")
    
    # 1. Register
    reg_resp = client.post("/auth/register", json={
        "email": "izumi@example.com",
        "password": "securepassword",
        "full_name": "Izumi"
    })
    print(f"Register: {reg_resp.status_code}")
    
    # 2. Login
    login_resp = client.post("/auth/login", data={
        "username": "izumi@example.com",
        "password": "securepassword"
    })
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print(f"Login: {login_resp.status_code}")
    
    # 3. Log "Anxious" Behavior (High screen time + high unlocks)
    behavior_resp = client.post("/behavior/log", headers=headers, json={
        "screen_time_seconds": 30000, # > 8 hours
        "unlock_count": 150,
        "app_usage": {"social_media": 15000, "work": 2000}
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
    assert data["emotional_state"] == "Distressed/Anxious" # Based on behavior logged earlier
    
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
