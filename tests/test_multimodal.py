import base64
import io
from PIL import Image
import numpy as np
import soundfile as sf
from backend.models.user import User
from sqlmodel import select

def create_dummy_image():
    # Create a small blank image
    img = Image.new('RGB', (100, 100), color=(255, 0, 0))
    buffered = io.BytesIO()
    img.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode()

def create_dummy_audio():
    # Create a short 1-second audio file (silent)
    path = "tests/dummy.wav"
    data = np.zeros(44100)
    sf.write(path, data, 44100)
    return path

def test_multimodal_endpoints(client, session):
    # 1. Register & Login
    client.post("/auth/register", json={"email": "multi@example.com", "password": "password123", "full_name": "Multi User"})
    
    user = session.exec(select(User).where(User.email == "multi@example.com")).first()
    user.is_verified = True
    session.commit()
    
    login_resp = client.post("/auth/login", data={"username": "multi@example.com", "password": "password123"})
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. Test Face Analysis (Base64)
    print("\nTesting /analyze/face...")
    img_b64 = create_dummy_image()
    face_resp = client.post("/analyze/face", headers=headers, data={"image_base64": img_b64})
    print(f"Face Result: {face_resp.json()}")
    
    # 3. Test Voice Analysis (File)
    print("\nTesting /analyze/voice...")
    audio_path = create_dummy_audio()
    with open(audio_path, "rb") as f:
        voice_resp = client.post("/analyze/voice", headers=headers, files={"audio_file": ("dummy.wav", f, "audio/wav")})
    print(f"Voice Result: {voice_resp.json()}")
    
    # 4. Test Multi-modal Chat
    print("\nTesting /chat with multi-modal data...")
    chat_resp = client.post("/chat/", headers=headers, json={
        "messages": [{"role": "user", "content": "I feel a mix of things."}],
        "face_emotion": "Happy",
        "voice_tone": "Neutral",
        "text_sentiment": 0.5
    })
    print(f"Chat Result: {chat_resp.json()}")

if __name__ == "__main__":
    test_multimodal_endpoints()
