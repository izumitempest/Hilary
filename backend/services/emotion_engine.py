import re
from typing import List, Dict, Any, Optional
from ..models.behavior import BehavioralData

STATE_SEVERITY = {
    "Critical Distress": 0,
    "Distressed/Anxious": 1,
    "Neutral": 2,
    "Calm/Content": 3,
    "Positive/Happy": 4,
}


class EmotionEngine:
    @staticmethod
    def normalize_face_emotion(raw: Optional[str]) -> Optional[str]:
        if not raw:
            return None
        key = re.sub(r"[^a-z]", "", raw.lower())
        mapping = {
            "happy": "Happy",
            "joy": "Happy",
            "sad": "Sad",
            "sorrow": "Sad",
            "anxious": "Anxious",
            "anxiety": "Anxious",
            "worried": "Anxious",
            "fear": "Anxious",
            "neutral": "Neutral",
            "calm": "Neutral",
            "angry": "Angry",
            "anger": "Angry",
            "surprised": "Surprised",
            "surprise": "Surprised",
        }
        for fragment, label in mapping.items():
            if fragment in key:
                return label
        return "Neutral"

    @staticmethod
    def resolve_final_state(
        preliminary: str,
        ai_detected: Optional[str],
        *,
        used_vision: bool = False,
    ) -> str:
        ai_state = ai_detected or preliminary
        if not used_vision:
            return ai_state
        pre_score = STATE_SEVERITY.get(preliminary, 2)
        ai_score = STATE_SEVERITY.get(ai_state, 2)
        chosen = min(pre_score, ai_score)
        for label, score in STATE_SEVERITY.items():
            if score == chosen:
                return label
        return preliminary

    @staticmethod
    def analyze_behavior(behaviors: List[BehavioralData]) -> str:
        """
        Derives an emotional state from screen time, unlocks, and categorized app usage.
        """
        if not behaviors:
            return "Neutral"
        
        data = behaviors[-1]
        
        # Categorize app usage
        social = 0
        productivity = 0
        entertainment = 0
        communication = 0
        health = 0
        
        for app_name, time_s in data.app_usage.items():
            app_lower = app_name.lower()
            if any(k in app_lower for k in ["instagram", "facebook", "tiktok", "twitter", "snapchat", "reddit", "threads"]):
                social += time_s
            elif any(k in app_lower for k in ["mail", "docs", "notes", "calendar", "slack", "teams", "office", "trello"]):
                productivity += time_s
            elif any(k in app_lower for k in ["youtube", "netflix", "spotify", "hulu", "disney", "game", "twitch"]):
                entertainment += time_s
            elif any(k in app_lower for k in ["whatsapp", "messages", "telegram", "messenger", "discord"]):
                communication += time_s
            elif any(k in app_lower for k in ["health", "fitness", "meditation", "calm", "headspace", "workout"]):
                health += time_s

        if data.screen_time_seconds > 28800 and data.unlock_count > 100:
            if social > 14400: # 4+ hours on social media
                return "Anxious/Overwhelmed"
            return "Slightly Stressed"
        elif data.screen_time_seconds < 3600 and data.unlock_count < 20:
            if health > 600: # Using health/meditation apps with low screen time
                return "Calm"
            return "Neutral"
        
        if social > 18000: # 5+ hours on social media
            return "Slightly Stressed"
            
        return "Neutral"

    @staticmethod
    def generate_behavior_insights(behaviors: List[BehavioralData]) -> str:
        """
        Generates a human-readable insights string for the LLM based on categorized app usage.
        """
        if not behaviors:
            return ""
        
        data = behaviors[-1]
        if not data.app_usage and data.screen_time_seconds == 0:
            return ""
            
        social, prod, ent, comm, health = 0, 0, 0, 0, 0
        for app_name, time_s in data.app_usage.items():
            app_lower = app_name.lower()
            if any(k in app_lower for k in ["instagram", "facebook", "tiktok", "twitter", "snapchat", "reddit"]): social += time_s
            elif any(k in app_lower for k in ["mail", "docs", "notes", "calendar", "slack", "teams"]): prod += time_s
            elif any(k in app_lower for k in ["youtube", "netflix", "spotify", "game"]): ent += time_s
            elif any(k in app_lower for k in ["whatsapp", "messages", "telegram"]): comm += time_s
            elif any(k in app_lower for k in ["health", "fitness", "meditation"]): health += time_s
            
        insights = []
        screen_hours = round(data.screen_time_seconds / 3600, 1)
        insights.append(f"Screen time in last window: {screen_hours} hours. Phone unlocks: {data.unlock_count}.")
        
        if social > 7200:
            insights.append(f"High social media usage ({round(social/3600, 1)} hrs) detected, which correlates with anxiety or comparison loops.")
        if ent > 10800 and prod < 1800:
            insights.append(f"High entertainment ({round(ent/3600, 1)} hrs) and low productivity usage suggests potential avoidance behavior or burnout.")
        if health > 0:
            insights.append(f"User actively engaged with health/wellness apps ({round(health/60, 1)} mins).")
        if data.unlock_count > 150:
            insights.append("High number of unlocks suggests compulsive phone checking or fragmented attention.")
            
        return " ".join(insights)

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
            "Anxious": -0.65,
            "Angry": -0.8,
            "Surprised": -0.15,
            "Excited": 0.7,
            "Agitated/Excited": -0.5,
            "Withdrawn/Low Energy": -0.4,
        }
        
        # Initial weights
        w_behavior = 0.2
        w_text = 0.3
        w_face = 0.25 if face_emotion else 0.0
        w_voice = 0.25 if voice_tone else 0.0
        
        # Normalize weights so they sum to 1.0
        total_weight = w_behavior + w_text + w_face + w_voice
        if total_weight > 0:
            w_behavior /= total_weight
            w_text /= total_weight
            w_face /= total_weight
            w_voice /= total_weight
            
        # Calculate base score from behavior
        score = label_map.get(behavior_state, 0.0) * w_behavior
        
        # Add text sentiment
        score += text_sentiment * w_text
        
        # Add face influence
        if face_emotion:
            normalized_face = EmotionEngine.normalize_face_emotion(face_emotion)
            score += label_map.get(normalized_face or "Neutral", 0.0) * w_face
            
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
