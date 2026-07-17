import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.pool import StaticPool
from backend.main import app
from backend.database import get_session
from backend.models.user import User
from backend.models.chat import ChatMessage
from backend.models.behavior import BehavioralData
from backend.models.alert import UserAlert

# Use in-memory SQLite for tests to isolate from hilary.db
TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    TEST_DATABASE_URL, 
    connect_args={"check_same_thread": False}, 
    poolclass=StaticPool
)

def override_get_session():
    with Session(engine) as session:
        yield session

app.dependency_overrides[get_session] = override_get_session

@pytest.fixture(autouse=True)
def mock_external_services(monkeypatch):
    from backend.services.email_service import email_service
    from backend.services.ai_service import ai_service
    
    monkeypatch.setattr(email_service, "send_verification_email", lambda email, token: True)
    
    async def mock_get_therapist_response(messages, current_state, face_emotion=None, behavior_insights=""):
        return {
            "response": "Mocked response",
            "detected_sentiment": current_state,  # Echo current state back for testing
            "intensity": 7.0,
            "insights": "Mocked insights"
        }
    monkeypatch.setattr(ai_service, "get_therapist_response", mock_get_therapist_response)
    
    async def mock_get_vision_emotion(image_b64):
        return "Happy"
    monkeypatch.setattr(ai_service, "get_vision_emotion", mock_get_vision_emotion)
    
    async def mock_get_audio_transcription(file_path):
        return "Mocked audio transcription"
    monkeypatch.setattr(ai_service, "get_audio_transcription", mock_get_audio_transcription)

@pytest.fixture(name="client")
def client_fixture():
    return TestClient(app)

@pytest.fixture(name="session", autouse=True)
def session_fixture():
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    SQLModel.metadata.drop_all(engine)
