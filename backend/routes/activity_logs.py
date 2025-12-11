from typing import List, Optional, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import SessionLocal
from models import ActivityLog
from schemas import ActivityLogOut

router = APIRouter(prefix="/activity", tags=["activity"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def log_activity(
    db: Session,
    proposal_id: Any,
    type: str,
    payload: dict,
    actor_id: Optional[str] = None,
):
    log = ActivityLog(
        proposal_id=proposal_id,
        actor_id=actor_id,
        type=type,
        payload=payload
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log

@router.get("/proposals/{proposal_id}", response_model=List[ActivityLogOut])
def list_activity_for_proposal(proposal_id: str, db: Session = Depends(get_db)):
    rows = (
        db.query(ActivityLog)
        .filter(ActivityLog.proposal_id == proposal_id)
        .order_by(ActivityLog.created_at)
        .all()
    )
    return rows