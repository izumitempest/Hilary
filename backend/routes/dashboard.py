from fastapi import APIRouter, Depends
from typing import List, Dict, Any
from sqlmodel import Session, select
from ..database import get_session
from ..models.user import User
from ..models.chat import ChatMessage
from ..models.behavior import BehavioralData
from .auth import get_current_user
from datetime import datetime, timedelta

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/summary")
async def get_dashboard_summary(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get an aggregated summary of the user's emotional and behavioral data.
    """
    # 1. Emotional Distribution (from Chat History)
    # We look at the last 30 days
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    
    # Query messages
    messages = session.exec(
        select(ChatMessage)
        .where(ChatMessage.user_id == current_user.id)
        .where(ChatMessage.timestamp >= thirty_days_ago)
    ).all()
    
    emotion_counts = {}
    for msg in messages:
        if msg.emotional_state:
            emotion_counts[msg.emotional_state] = emotion_counts.get(msg.emotional_state, 0) + 1
            
    # 2. Behavioral Trends
    behaviors = session.exec(
        select(BehavioralData)
        .where(BehavioralData.user_id == current_user.id)
        .where(BehavioralData.timestamp >= thirty_days_ago)
        .order_by(BehavioralData.timestamp.asc())
    ).all()
    
    behavior_history = []
    for b in behaviors:
        behavior_history.append({
            "timestamp": b.timestamp,
            "screen_time": b.screen_time_seconds,
            "unlocks": b.unlock_count
        })
        
    return {
        "emotion_distribution": emotion_counts,
        "behavior_history": behavior_history,
        "total_sessions": len(messages) // 2, # Rough estimate (user + assistant)
        "last_detected_state": messages[-1].emotional_state if messages else "Neutral"
    }
