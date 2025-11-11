from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class ClientCreate(BaseModel):
    name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None

class ClientOut(BaseModel):
    name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    created_at = datetime
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

        
