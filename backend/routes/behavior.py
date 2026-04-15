from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from ..database import get_session
from ..models.behavior import BehavioralData, BehavioralDataCreate
from ..models.user import User
from .auth import get_current_user

router = APIRouter(prefix="/behavior", tags=["Behavior"])

@router.post("/log")
def log_behavior(
    behavior_in: BehavioralDataCreate, 
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    db_behavior = BehavioralData(
        user_id=current_user.id,
        screen_time_seconds=behavior_in.screen_time_seconds,
        app_usage=behavior_in.app_usage,
        unlock_count=behavior_in.unlock_count
    )
    session.add(db_behavior)
    session.commit()
    session.refresh(db_behavior)
    return {"status": "success", "id": db_behavior.id}

@router.get("/summary")
def get_behavior_summary(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # For now, just return all logs for the current user
    # Later we will implement aggregation logic here
    return current_user.behaviors
