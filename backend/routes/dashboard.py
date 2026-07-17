from fastapi import APIRouter, Depends
from typing import List, Dict, Any
from sqlmodel import Session, select
from ..database import get_session
from ..models.user import User
from ..models.chat import ChatMessage
from ..models.behavior import BehavioralData
from .auth import get_current_user
from datetime import datetime, timedelta, timezone

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
    thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
    
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
    social, prod, ent, comm, health = 0, 0, 0, 0, 0
    total_screen_time = 0
    
    for b in behaviors:
        behavior_history.append({
            "timestamp": b.timestamp,
            "screen_time": b.screen_time_seconds,
            "unlocks": b.unlock_count
        })
        total_screen_time += b.screen_time_seconds
        for app_name, time_s in (b.app_usage or {}).items():
            app_lower = app_name.lower()
            if any(k in app_lower for k in ["instagram", "facebook", "tiktok", "twitter", "snapchat", "reddit"]): social += time_s
            elif any(k in app_lower for k in ["mail", "docs", "notes", "calendar", "slack", "teams"]): prod += time_s
            elif any(k in app_lower for k in ["youtube", "netflix", "spotify", "game"]): ent += time_s
            elif any(k in app_lower for k in ["whatsapp", "messages", "telegram"]): comm += time_s
            elif any(k in app_lower for k in ["health", "fitness", "meditation"]): health += time_s

    # Compute a simple Wellbeing Score (0-100)
    # Higher is better. Based on balanced app usage and positive emotional states
    score = 70 # Base score
    if total_screen_time > 0:
        social_ratio = social / total_screen_time
        if social_ratio > 0.4: score -= 15
        elif social_ratio > 0.2: score -= 5
        
        health_ratio = health / total_screen_time
        if health_ratio > 0.05: score += 10
        
    pos_states = emotion_counts.get("Positive/Happy", 0) + emotion_counts.get("Calm/Content", 0)
    neg_states = emotion_counts.get("Critical Distress", 0) + emotion_counts.get("Distressed/Anxious", 0) + emotion_counts.get("Sad", 0) + emotion_counts.get("Angry", 0)
    total_emotions = sum(emotion_counts.values())
    if total_emotions > 0:
        score += (pos_states / total_emotions) * 20
        score -= (neg_states / total_emotions) * 20
        
    score = max(0, min(100, int(score)))
        
    return {
        "emotion_distribution": emotion_counts,
        "behavior_history": behavior_history,
        "app_breakdown": {
            "Social": social,
            "Productivity": prod,
            "Entertainment": ent,
            "Communication": comm,
            "Health & Wellness": health
        },
        "wellbeing_score": score,
        "total_sessions": len(messages) // 2, # Rough estimate (user + assistant)
        "last_detected_state": messages[-1].emotional_state if messages else "Neutral"
    }
