from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Client
from schemas import ClientCreate, ClientOut

router = APIRouter(prefix="/clients", tags=["clients"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=ClientOut)
def create_client(payload: ClientCreate, db: Session = Depends(get_db)):
    c = Client(
        name=payload.name, 
        email=payload.email, 
        phone=payload.phone)
    db.add(c)
    db.commit()
    db.refresh(c)
    return c

@router.get("/", response_model=list[ClientOut])
def list_clients(db: Session = Depends(get_db)):
    rows = db.query(Client).all()
    return rows