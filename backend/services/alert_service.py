from sqlmodel import Session
from ..models.alert import UserAlert

class AlertService:
    @staticmethod
    def trigger_alert(session: Session, user_id: int, state: str):
        """
        Evaluate if a state transition or a specific state deserves an alert.
        """
        if state == "Critical Distress":
            alert = UserAlert(
                user_id=user_id,
                severity="CRITICAL",
                message="Critical emotional distress detected. Please reach out for support or use our crisis resources."
            )
            session.add(alert)
            # In a real app, this would also send a Push Notification or Email
            print(f"!!! CRITICAL ALERT for user {user_id} !!!")
        
        elif state == "Distressed/Anxious":
            # Check if we already have a warning recently?
            alert = UserAlert(
                user_id=user_id,
                severity="WARNING",
                message="We've noticed you're feeling a bit overwhelmed. Would you like to try a breathing exercise?"
            )
            session.add(alert)

alert_service = AlertService()
