from typing import Optional
from sqlmodel import SQLModel, Field
from datetime import datetime

class UserAlert(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    severity: str # "INFO", "WARNING", "CRITICAL"
    message: str
    is_resolved: bool = Field(default=False)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
