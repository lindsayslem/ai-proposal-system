from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Proposal, Project, ProposalVersion
from schemas import(ProposalCreate, ProposalOut, ProposalVersionCreate, ProposalVersionOut)
from routes.activity_logs import log_activity
from models import Proposal, ProposalLineItem, ProposalVersion
from openai import OpenAI
client = OpenAI()

router = APIRouter(prefix="/proposals", tags=["proposals"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally: db.close()

@router.post("/", response_model=ProposalOut)
def create_proposal(payload: ProposalCreate, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == payload.project_id).first()
    if not project:
        raise HTTPException(status_code=400, detail="Project not found")
    
    proposal = Proposal(project_id=payload.project_id)
    db.add(proposal)
    db.commit()
    db.refresh(proposal)

    log_activity(
        db,
        proposal_id=proposal.id,
        type="proposal_created",
        payload={"project_id": proposal.project_id},
    )
    return proposal

@router.get("/", response_model=List[ProposalOut])
def list_proposals(db: Session = Depends(get_db)):
    rows = db.query(Proposal).all()
    return rows

@router.post("/{proposal_id}/versions", response_model=ProposalVersionOut)
def create_version(
    proposal_id: str,
    payload: ProposalVersionCreate,
    db: Session = Depends(get_db),
):
    proposal = db.query(Proposal).filter(Proposal.id == proposal_id).first()
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")
    
    next_num = len(proposal.versions) + 1

    v = ProposalVersion(
        proposal_id=proposal_id,
        version_num=next_num,
        ai_summary=payload.ai_summary,
        terms=payload.terms,
        valid_until=payload.valid_until,
    )
    db.add(v)
    db.commit()
    db.refresh(v)

    log_activity(
        db,
        proposal_id=proposal.id,
        type="version_created",
        payload={"version_id": v.id, "version_num": v.version_num},
    )

    return v

@router.get("/{proposal_id}/versions", response_model=List[ProposalVersionOut])
def list_versions(proposal_id: str, db: Session = Depends(get_db)):
    rows = (
        db.query(ProposalVersion)
        .filter(ProposalVersion.proposal_id == proposal_id)
        .order_by(ProposalVersion.version_num)
        .all()
    )
    return rows

@router.get("/{proposal_id}/full")
def get_full_proposal(proposal_id: str, db: Session = Depends(get_db)):
    proposal = (
        db.query(Proposal)
        .filter(Proposal.id == proposal_id)
        .first()
    )
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")

    version = proposal.current_version or (
        proposal.versions[0] if proposal.versions else None
    )

    items = []
    if version:
        items = (
            db.query(ProposalLineItem)
            .filter(ProposalLineItem.proposal_version_id == version.id)
            .order_by(ProposalLineItem.position)
            .all()
        )

    return {
        "proposal": proposal,
        "project": proposal.project,
        "version": version,
        "line_items": items,
    }

@router.post("/{proposal_id}/ai-summary")
def generate_ai_summary(proposal_id: str, db: Session = Depends(get_db)):
    proposal = db.query(Proposal).filter(Proposal.id == proposal_id).first()
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")

    version = (
        db.query(ProposalVersion)
        .filter(ProposalVersion.proposal_id == proposal_id)
        .order_by(ProposalVersion.version_num.desc())
        .first()
    )

    if not version:
        raise HTTPException(status_code=400, detail="No proposal versions exist")

    prompt = f"""
    Summarize this proposal in a professional tone:

    TERMS:
    {version.terms}
    """

    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[{"role": "user", "content": prompt}]
    )

    ai_summary = response.choices[0].message.content

    version.ai_summary = ai_summary
    db.commit()
    db.refresh(version)

    return {"summary": ai_summary}
