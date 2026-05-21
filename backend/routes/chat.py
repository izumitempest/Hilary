from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict
from sqlmodel import Session
from ..database import get_session
from ..models.user import User
from .auth import get_current_user
from ..services.ai_service import ai_service
from ..services.emotion_engine import emotion_engine
from pydantic import BaseModel
from typing import List, Dict, Optional

class ChatRequest(BaseModel):
    messages: List[Dict[str, str]]
    face_emotion: Optional[str] = None
    voice_tone: Optional[str] = None
    text_sentiment: float = 0.0
    image_b64: Optional[str] = None

router = APIRouter(prefix="/chat", tags=["Chat"])

from ..models.chat import ChatMessage

@router.post("/")
async def chat(
    request: ChatRequest, 
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # 1. Get behavioral context
    behaviors = current_user.behaviors
    behavioral_state = emotion_engine.analyze_behavior(behaviors)
    
    # 2. Extract initial heuristic sentiment
    text_sentiment = request.text_sentiment
    if text_sentiment == 0.0 and request.messages:
        last_msg = request.messages[-1].get("content", "").lower()
        neg_words = ["sad", "depress", "kill", "die", "hurt", "pain", "anxious", "scared", "hate", "worthless", "empty", "lonely"]
        pos_words = ["happy", "good", "great", "better", "excited", "love", "joy", "hope", "thanks", "calm"]
        
        score = 0.0
        for w in neg_words:
            if w in last_msg: score -= 0.6
        for w in pos_words:
            if w in last_msg: score += 0.4
        if "kill myself" in last_msg or "hurt myself" in last_msg or "end it" in last_msg:
            score -= 2.0
            
        text_sentiment = max(-1.0, min(1.0, score))

    # 3. Process Vision Modality if image provided
    face_emotion = request.face_emotion
    vision_source = None
    if request.image_b64:
        raw_face = await ai_service.get_vision_emotion(request.image_b64)
        face_emotion = emotion_engine.normalize_face_emotion(raw_face)
        vision_source = ai_service.vision_backend if request.image_b64 else None

    # 4. Perform Multi-modal Fusion (Preliminary)
    preliminary_state = emotion_engine.multi_modal_fusion(
        behavior_state=behavioral_state,
        text_sentiment=text_sentiment,
        face_emotion=face_emotion,
        voice_tone=request.voice_tone
    )
    
    # 5. Get response from Groq (Now returns JSON with sentiment)
    ai_data = await ai_service.get_therapist_response(
        request.messages,
        preliminary_state,
        face_emotion=face_emotion,
    )
    
    final_state = emotion_engine.resolve_final_state(
        preliminary_state,
        ai_data.get("detected_sentiment"),
        used_vision=bool(request.image_b64),
    )
    ai_response = ai_data.get("response", "I'm listening.")
    ai_insights = ai_data.get("insights", "")
    
    # 6. Persist Conversation
    if request.messages:
        last_user_msg = request.messages[-1]
        content = (last_user_msg.get("content") or "").strip()
        if request.image_b64:
            if not content:
                content = "[Photo shared for emotional analysis]"
            elif "[Photo" not in content:
                content = f"{content}\n[Photo attached]"
        user_msg_db = ChatMessage(
            user_id=current_user.id,
            role="user",
            content=content,
            emotional_state=final_state,
            insights=None
        )
        session.add(user_msg_db)
    
    assistant_msg_db = ChatMessage(
        user_id=current_user.id,
        role="assistant",
        content=ai_response,
        emotional_state=final_state,
        insights=ai_insights
    )
    session.add(assistant_msg_db)
    
    # 6. Proactive Alerts
    from ..services.alert_service import alert_service
    alert_service.trigger_alert(session, current_user.id, final_state)
    
    session.commit()
    
    return {
        "response": ai_response,
        "emotional_state": final_state,
        "insights": ai_insights,
        "intensity": ai_data.get("intensity", 5.0),
        "face_emotion": face_emotion,
        "vision_source": vision_source,
        "preliminary_state": preliminary_state,
    }

@router.get("/history", response_model=List[ChatMessage])
async def get_history(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    from sqlmodel import select
    # Explicitly fetch to avoid relationship lazy-loading issues
    messages = session.exec(
        select(ChatMessage).where(ChatMessage.user_id == current_user.id)
    ).all()
    return messages

@router.delete("/history")
async def clear_history(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    for msg in current_user.messages:
        session.delete(msg)
    session.commit()
    return {"status": "cleared"}
