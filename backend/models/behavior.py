from typing import Optional, Dict, Any
from sqlmodel import SQLModel, Field, Relationship, JSON
from datetime import datetime, timezone
from .user import User

class BehavioralData(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Usage metrics
    screen_time_seconds: int
    app_usage: Dict[str, Any] = Field(default={}, sa_type=JSON)
    unlock_count: int
    
    # Emotional context detected from patterns
    inferred_mood: Optional[str] = None
    mood_confidence: Optional[float] = None
    
    user: User = Relationship(back_populates="behaviors")

class BehavioralDataCreate(SQLModel):
    screen_time_seconds: int
    app_usage: Dict[str, Any]
    unlock_count: int
