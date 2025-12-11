from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import SessionLocal
from models import Attachment, Proposal
from schemas import AttachmentCreate, AttachmentOut

router = APIRouter(prefix="/attachments", tags=["attachments"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=AttachmentOut)
def create_attachment(payload: AttachmentCreate, db: Session = Depends(get_db)):
    proposal = (db.query(Proposal)
                .filter(Proposal.id == payload.propposal_id)
                .first()
            )
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")
    
    att = Attachment(
        proposal_id=payload.propposal_id,
        file_url=payload.file_url,
        file_type=payload.file_type,
        uploaded_by=payload.uploaded_by,
    )
    db.add(att)
    db.commit()
    db.refresh(att)
    return att

@router.get("/by-proposal/{proposal_id}", response_model=List[AttachmentOut])
def list_attachments_for_proposal(proposal_id: str, db: Session = Depends(get_db)):
    rows = (
        db.query(Attachment)
        .filter(Attachment.proposal_id == proposal_id)
        .order_by(Attachment.uploaded_at)
        .all()
    )
    return rows
