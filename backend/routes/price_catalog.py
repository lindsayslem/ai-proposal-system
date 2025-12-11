from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import SessionLocal
from models import PriceCatalogItem
from schemas import PriceCatalogItemCreate, PriceCatalogItemOut

router = APIRouter(prefix="/catalog", tags=["catalog"])

def get_db():
    db = SessionLocal()
    try: 
        yield db
    finally:
        db.close()

@router.post("/", response_model=PriceCatalogItemOut)
def create_item(payload: PriceCatalogItemCreate, db: Session = Depends(get_db)):
    item = PriceCatalogItem(**payload.dict())
    db.add(item)
    db.commit()
    db.refresh(item)

    return item

@router.get("/", response_model=list[PriceCatalogItemOut])
def list_items(db: Session = Depends(get_db)):
    return db.query(PriceCatalogItem).all()