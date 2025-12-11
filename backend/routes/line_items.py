from typing import List 
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models import ProposalLineItem, ProposalVersion, Proposal
from schemas import LineItemCreate, LineItemOut
from routes.activity_logs import log_activity

router = APIRouter(prefix="/line-items", tags=['line_items'])

def get_db():
    db = SessionLocal()
    try: 
        yield db
    finally:
        db.close()

def recalc_proposal_totals(db: Session, proposal: Proposal):
    if proposal.current_version_id is None:
        return
    
    version = (
        db.query(ProposalVersion)
        .filter(ProposalVersion.id == proposal.current_version_id)
        .first()
    )
    if not version:
        return
    
    items = (
        db.query(ProposalLineItem)
        .filter(ProposalLineItem.proposal_version_id == version.id)
        .all()
    )

    subtotal = sum(item.line_total for item in items)
    tax = 0.0
    total = subtotal + tax

    proposal.subtotal = subtotal
    proposal.tax = tax
    proposal.total = total
    db.add(proposal)
    db.commit()
    db.refresh(proposal)

@router.post("/", response_model=LineItemOut)
def create_line_item(payload: LineItemCreate, db: Session = Depends(get_db)):
    version = (
        db.query(ProposalVersion)
        .filter(ProposalVersion.id == payload.proposal_version_id)
        .first()
    )
    if version is None:
        raise HTTPException(status_code=404, detail="Proposal version not found")
    
    line_total = payload.qty * payload.unit_price

    existing_count = (
        db.query(ProposalLineItem)
        .filter(ProposalLineItem.proposal_version_id == payload.proposal_version_id)
        .count()
    )

    item = ProposalLineItem(
        proposal_version_id=payload.proposal_version_id,
        name=payload.name,
        qty=payload.qty,
        unit_price=payload.unit_price,
        line_total=line_total,
        position=existing_count + 1,
    )

    db.add(item)
    db.commit()
    db.refresh(item)

    proposal = version.proposal
    recalc_proposal_totals(db, proposal)

    return item

@router.get(
    "/by-version/{version_id}",
    response_model=List[LineItemOut]
)    
def list_items_for_version(version_id: str, db: Session = Depends(get_db)):
    rows = (
        db.query(ProposalLineItem)
        .filter(ProposalLineItem.proposal_version_id == version_id)
        .order_by(ProposalLineItem.position)
        .all()
    )
    return rows
