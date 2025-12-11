from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict
from datetime import datetime

class ClientCreate(BaseModel):
    name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None

class ClientOut(BaseModel):
    id: str
    name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    created_at: datetime
    class Config:
        from_attributes = True

class ProjectCreate(BaseModel):
    client_id: str
    title: str
    status: str = "lead"

class ProjectOut(BaseModel):
    id: str
    client_id: str
    title: str
    status: str
    created_at: datetime
    class Config:
        from_attributes = True

class ProposalCreate(BaseModel):
    project_id: str

class ProposalOut(BaseModel):
    id: str
    project_id: str
    status: str
    subtotal: float
    tax: float
    total: float
    created_at: datetime

    class Config:
        from_attributes = True

class ProposalVersionCreate(BaseModel):
    ai_summary: Optional[str] = None
    terms: Optional[str] = None
    valid_until: Optional[datetime] = None

class ProposalVersionOut(BaseModel):
    id: str
    proposal_id: str
    version_num: int
    ai_summary: Optional[str] = None
    terms: Optional[str] = None
    valid_until: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True

class PriceCatalogItemCreate(BaseModel):
    sku: str
    name: str
    category: str | None = None
    unit: str | None = None
    unit_cost: float = 0.0
    unit_price: float = 0.0

class PriceCatalogItemOut(PriceCatalogItemCreate):
    id: str
    is_active: bool
    last_sync_at: datetime

    class Config:
        from_attributes = True

class LineItemCreate(BaseModel):
    proposal_version_id: str
    name: str
    qty: float = 1.0
    unit_price: float = 0.0

class LineItemOut(BaseModel):
    id: str
    proposal_version_id: str
    name: str
    qty: float
    unit_price: float
    line_total: float
    position: int
    created_at: datetime

    class Config:
        from_attributes = True

class AttachmentCreate(BaseModel):
    propposal_id: str
    file_url: str
    file_type: Optional[str] = None
    uploaded_by: Optional[str] = None

class AttachmentOut(BaseModel):
    id: str
    proposal_id: str
    file_url: str
    file_type: Optional[str] = None
    uploaded_by: Optional[str] = None
    uploaded_at: datetime

    class Config:
        from_attributes = True

class ActivityLogOut(BaseModel):
    id: str
    proposal_id: str
    actor_id: Optional[str] = None
    type: str
    payload: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

