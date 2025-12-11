from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Project, Client
from schemas import ProjectCreate, ProjectOut

router = APIRouter(prefix="/projects", tags=["projects"])

def get_db():
    db = SessionLocal()
    try: 
        yield db
    finally:
        db.close()

@router.post("/", response_model=ProjectOut)
def create_project(payload: ProjectCreate, db: Session = Depends(get_db)):
    client = db.query(Client).filter(Client.id == payload.client_id).first()
    if client is None:
        raise HTTPException(status_code=404, detail="Client not found")
    
    p = Project(
        client_id=payload.client_id,
        title=payload.title,
        status=payload.status,
    )
    db.add(p)
    db.commit()
    db.refresh(p)
    return p

@router.get("/", response_model=list[ProjectOut])
def list_projects(db: Session = Depends(get_db)):
    rows = db.query(Project).all()
    return rows
