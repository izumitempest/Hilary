from typing import Optional
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime, timezone

class UserAlert(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    severity: str # "LOW", "MEDIUM", "HIGH", "CRITICAL"
    message: str
    is_resolved: bool = Field(default=False)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Relationship back to the user
    user: Optional["User"] = Relationship(back_populates="alerts")
