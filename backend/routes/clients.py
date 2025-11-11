from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Client

router = APIRouter(prefix="/clients", tags=["clients"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=dict)
def create_client(payload: dict, db: Session = Depends(get_db)):
    c = Client(name=payload["name"], email=payload.get("email"), phone=payload.get("phone"))
    db.add(c); db.commit(); db.refresh(c)
    return {"id": c.id, "name": c.name, "email": c.email, "phone": c.phone}

@router.get("/", response_model=list[dict])
def list_clients(db: Session = Depends(get_db)):
    rows = db.query(Client).all()
    return [{"id": r.id, "name": r.name, "email": r.email, "phone": r.phone} for r in rows]