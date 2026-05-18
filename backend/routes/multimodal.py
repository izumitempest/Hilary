import os
import uuid
from fastapi import APIRouter, Depends, UploadFile, File, Form
from typing import Optional
from ..services.ai_service import ai_service
from ..services.emotion_engine import emotion_engine
from ..services.audio_utils import audio_utils
from ..models.user import User
from .auth import get_current_user

router = APIRouter(prefix="/analyze", tags=["Multi-Modal"])

# Persistent directory for media storage
MEDIA_DIR = "media"
os.makedirs(MEDIA_DIR, exist_ok=True)

@router.post("/face")
async def analyze_face(
    image_base64: str = Form(...),
    current_user: User = Depends(get_current_user)
):
    """Analyze face from base64 image and return detected emotion."""
    raw = await ai_service.get_vision_emotion(image_base64)
    emotion = emotion_engine.normalize_face_emotion(raw)
    model_source = "pytorch" if ai_service.custom_vision_model else "groq-vision"
    return {"emotion": emotion, "raw_emotion": raw, "source": "face", "model_source": model_source}

@router.post("/voice")
async def analyze_voice(
    audio_file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """Analyze voice (Tone + Transcription) from audio file."""
    # Save file persistently in media/
    file_id = str(uuid.uuid4())
    ext = audio_file.filename.split(".")[-1]
    storage_path = os.path.join(MEDIA_DIR, f"{file_id}.{ext}")
    
    with open(storage_path, "wb") as buffer:
        buffer.write(await audio_file.read())
    
    try:
        # 1. Linguistic Sentiment (Whisper)
        transcript = await ai_service.get_audio_transcription(storage_path)
        
        # 2. Acoustic Analysis (Prosody)
        features = audio_utils.get_prosody_features(storage_path)
        tone = audio_utils.classify_tone(features)
        
        return {
            "transcript": transcript,
            "tone": tone,
            "source": "voice",
            "metadata": {"file_id": file_id, "file_path": storage_path}
        }
    except Exception as e:
        return {"error": str(e), "source": "voice"}
