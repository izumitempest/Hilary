from typing import Optional
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime, timezone
from .user import User

class ChatMessage(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    role: str # "user" or "assistant"
    content: str
    emotional_state: Optional[str] = None # The state detected at the time
    insights: Optional[str] = None # AI-generated analysis of the state
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Relationship
    user: User = Relationship(back_populates="messages")
