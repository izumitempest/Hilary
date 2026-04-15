from typing import List, Dict, Any, Optional
from ..models.behavior import BehavioralData


class EmotionEngine:
    @staticmethod
    def analyze_behavior(data: List[BehavioralData]) -> str:
        if not data:
            return "Neutral"
        
        # Simple heuristic-based engine
        # In a real app, this would be a more complex ML model
        
        # Get the latest entry
        latest = data[-1]
        
        # Patterns indicative of high stress/anxiety
        # 1. High screen time late at night
        # 2. Frequent unlocks
        # 3. Long usage of social media apps (indicated in app_usage)
        
        stress_score = 0
        
        # Screen time check (e.g., > 6 hours a day is high)
        if latest.screen_time_seconds > 21600:
            stress_score += 1
            
        # Unlock count check (e.g., > 100 times a day is frequent)
        if latest.unlock_count > 100:
            stress_score += 1
            
        # Decision mapping
        if stress_score >= 2:
            return "Anxious/Overwhelmed"
        elif stress_score == 1:
            return "Slightly Stressed"
        
        return "Calm"

    @staticmethod
    def multi_modal_fusion(
        behavior_state: str,
        text_sentiment: float = 0.0,
        face_emotion: Optional[str] = None,
        voice_tone: Optional[str] = None
    ) -> str:
        """
        Produce a unified emotional state string based on weighted inputs.
        """
        # Map labels to scores (-1.0 to 1.0)
        label_map = {
            "Anxious/Overwhelmed": -0.7,
            "Slightly Stressed": -0.3,
            "Calm": 0.2,
            "Neutral": 0.0,
            "Happy": 0.8,
            "Sad": -0.6,
            "Angry": -0.8,
            "Excited": 0.7,
            "Agitated/Excited": -0.5, # Often negative in therapy context
            "Withdrawn/Low Energy": -0.4
        }
        
        # Initial weights
        w_behavior = 0.2
        w_text = 0.3
        w_face = 0.25
        w_voice = 0.25
        
        # Calculate base score from behavior
        score = label_map.get(behavior_state, 0.0) * w_behavior
        
        # Add text sentiment
        score += text_sentiment * w_text
        
        # Add face influence
        if face_emotion:
            score += label_map.get(face_emotion, 0.0) * w_face
            
        # Add voice influence
        if voice_tone:
            score += label_map.get(voice_tone, 0.0) * w_voice
            
        # Final classification
        if score <= -0.6:
            return "Critical Distress"
        elif score <= -0.3:
            return "Distressed/Anxious"
        elif score >= 0.5:
            return "Positive/Happy"
        elif score >= 0.2:
            return "Calm/Content"
        
        return "Neutral"

emotion_engine = EmotionEngine()
