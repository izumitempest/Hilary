from backend.services.emotion_engine import emotion_engine
from backend.models.behavior import BehavioralData
from datetime import datetime

def test_analyze_behavior_calm():
    data = [
        BehavioralData(
            user_id=1, 
            screen_time_seconds=1000, 
            unlock_count=15, 
            app_usage={"headspace": 700}
        )
    ]
    assert emotion_engine.analyze_behavior(data) == "Calm"

def test_analyze_behavior_anxious():
    # > 6 hours (21600s) and > 100 unlocks
    data = [
        BehavioralData(
            user_id=1, 
            screen_time_seconds=30000, 
            unlock_count=120, 
            app_usage={"tiktok": 15000}
        )
    ]
    assert emotion_engine.analyze_behavior(data) == "Anxious/Overwhelmed"

def test_fusion_score():
    state = "Anxious/Overwhelmed"
    # Negative sentiment + Angry face to reach Critical Distress
    # score = (-0.7 * 0.2) + (-1.0 * 0.3) + (-0.8 * 0.25) = -0.14 - 0.3 - 0.2 = -0.64
    assert emotion_engine.multi_modal_fusion(state, text_sentiment=-1.0, face_emotion="Angry") == "Critical Distress"
    
    # Just anxious behavior + negative sentiment = Critical Distress (due to correct weight normalization)
    # score = -0.7 * (0.2/0.5) + -0.8 * (0.3/0.5) = -0.28 + -0.48 = -0.76 (<= -0.6)
    assert emotion_engine.multi_modal_fusion(state, text_sentiment=-0.8) == "Critical Distress"
    
    # Positive sentiment
    # score = -0.14 + (0.8 * 0.3) = -0.14 + 0.24 = 0.1 (Neutral)
    # To get Positive/Happy (>= 0.5), we need more:
    # score = (-0.7 * 0.2) + (1.0 * 0.3) + (0.8 * 0.25) + (0.8 * 0.25) = -0.14 + 0.3 + 0.2 + 0.2 = 0.56
    assert emotion_engine.multi_modal_fusion(state, text_sentiment=1.0, face_emotion="Happy", voice_tone="Happy") == "Positive/Happy"
    
    # Neutral sentiment fallback
    assert emotion_engine.multi_modal_fusion(state, text_sentiment=0) == "Neutral"
