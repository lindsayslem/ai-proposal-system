from sqlalchemy import Column, String, Enum, DateTime, ForeignKey, Float, Text, Integer, Boolean, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from database import Base

def gen_id():
    return str(uuid.uuid4())

class Employee(Base):
    __tablename__ = "employees"
    id = Column(String, primary_key=True, default=gen_id)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(Enum("sales_rep", "admin", name="employee_roles"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Client(Base):
    __tablename__ = "clients"
    id = Column(String, primary_key=True, default=gen_id)
    name = Column(String, nullable=False)
    email = Column(String)
    phone = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    projects = relationship("Project", back_populates="client", cascade="all, delete-orphan")

class Project(Base):
    __tablename__ = "projects"
    id = Column(String, primary_key=True, default=gen_id)
    client_id = Column(String, ForeignKey("clients.id", ondelete="RESTRICT"), nullable=False)
    title = Column(String, nullable=False)
    status = Column(String, default="lead")
    created_at = Column(DateTime, default=datetime.utcnow)
    client = relationship("Client", back_populates="projects")

class Proposal(Base):
    __tablename__ = "proposals"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    status = Column(String, default="draft")
    current_version_id = Column(String, ForeignKey("proposal_versions.id"), nullable=True)
    subtotal = Column(Float, default=0.0)
    tax = Column(Float, default=0.0)
    total = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    project = relationship("Project", backref='proposals')
    versions = relationship(
        "ProposalVersion",
        back_populates="proposal",
        cascade="all, delete-orphan",
        foreign_keys="ProposalVersion.proposal_id",
    )
    current_version = relationship(
        "ProposalVersion",
        foreign_keys=[current_version_id],
        uselist=False,
    )
    activity_logs = relationship(
        "ActivityLog",
        back_populates="proposal",
        cascade="all, delete-orphan",
    )

class ProposalVersion(Base):
    __tablename__ = "proposal_versions"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    proposal_id = Column(String, ForeignKey("proposals.id"), nullable=False)
    version_num = Column(Integer, nullable=False)
    ai_summary = Column(Text)
    terms = Column(Text)
    valid_until = Column(DateTime, nullable=True)
    created_by = Column(String, ForeignKey("employees.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    proposal = relationship("Proposal", back_populates="versions", foreign_keys=[proposal_id])
    line_items = relationship("ProposalLineItem", back_populates="version", cascade="all, delete-orphan",)

class ProposalLineItem(Base):
    __tablename__ = "proposal_line_items"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    proposal_version_id = Column(String, ForeignKey("proposal_versions.id"), nullable=False,)
    name = Column(String, nullable=False)        
    qty = Column(Float, nullable=False, default=1)
    unit_price = Column(Float, nullable=False, default=0.0)
    line_total = Column(Float, nullable=False, default=0.0)
    position = Column(Integer, nullable=False, default=0) 
    created_at = Column(DateTime, default=datetime.utcnow)
    version = relationship("ProposalVersion", back_populates="line_items")

class PriceCatalogItem(Base):
    __tablename__ = "price_catalog_items"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    sku = Column(String, nullable=False)
    name = Column(String, nullable=False)
    category = Column(String)
    unit = Column(String)
    unit_cost = Column(Float, default=0.0)
    unit_price = Column(Float, default=0.0)
    is_active = Column(Boolean, default=True)
    last_sync_at = Column(DateTime, default=datetime.utcnow)

class Attachment(Base):
    __tablename__ = "attachments"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    proposal_id = Column(String, ForeignKey("proposals.id"), nullable=False)
    file_url = Column(String, nullable=False)
    file_type = Column(String, nullable=True)
    uploaded_by = Column(String, ForeignKey("employees.id"), nullable=True)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    proposal = relationship("Proposal", backref="attachments")

class ActivityLog(Base):
    __tablename__ = "activity_logs"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    proposal_id = Column(String, ForeignKey("proposals.id"), nullable=False)
    actor_id = Column(String, ForeignKey("employees.id"), nullable=True)
    type = Column(String, nullable=False)
    payload = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    proposal = relationship("Proposal", back_populates="activity_logs")