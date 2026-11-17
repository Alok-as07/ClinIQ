import uuid

from datetime import datetime, timezone

from sqlalchemy import (
    String,
    DateTime,
    ForeignKey,
    Text,
    Float,
    JSON,
    Boolean
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship
)

from app.db.base import Base


def generate_id():
    return str(uuid.uuid4())


def current_time():
    return datetime.now(timezone.utc)


class Tenant(Base):

    __tablename__ = "tenants"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=generate_id
    )

    name: Mapped[str] = mapped_column(
        String(160),
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=current_time
    )


class User(Base):

    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=generate_id
    )

    tenant_id: Mapped[str] = mapped_column(
        ForeignKey("tenants.id"),
        index=True
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True
    )

    full_name: Mapped[str] = mapped_column(
        String(160)
    )

    password_hash: Mapped[str] = mapped_column(
        String(255)
    )

    role: Mapped[str] = mapped_column(
        String(40),
        default="CLINICIAN"
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=current_time
    )


class Patient(Base):

    __tablename__ = "patients"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=generate_id
    )

    tenant_id: Mapped[str] = mapped_column(
        ForeignKey("tenants.id"),
        index=True
    )

    display_name: Mapped[str] = mapped_column(
        String(160)
    )

    external_ref: Mapped[str | None] = mapped_column(
        String(80),
        nullable=True
    )

    date_of_birth: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True
    )

    sex: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=current_time
    )

    documents: Mapped[list["ClinicalDocument"]] = relationship(
        back_populates="patient"
    )


class ClinicalDocument(Base):

    __tablename__ = "clinical_documents"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=generate_id
    )

    tenant_id: Mapped[str] = mapped_column(
        ForeignKey("tenants.id"),
        index=True
    )

    patient_id: Mapped[str] = mapped_column(
        ForeignKey("patients.id"),
        index=True
    )

    uploaded_by: Mapped[str] = mapped_column(
        ForeignKey("users.id")
    )

    filename: Mapped[str] = mapped_column(
        String(255)
    )

    encrypted_path: Mapped[str] = mapped_column(
        String(500)
    )

    document_type: Mapped[str] = mapped_column(
        String(50),
        default="OTHER"
    )

    processing_status: Mapped[str] = mapped_column(
        String(40),
        default="UPLOADED"
    )

    redacted_text: Mapped[str] = mapped_column(
        Text,
        default=""
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=current_time
    )

    patient: Mapped[Patient] = relationship(
        back_populates="documents"
    )

    observations: Mapped[list["Observation"]] = relationship(
        back_populates="document"
    )


class Observation(Base):

    __tablename__ = "observations"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=generate_id
    )

    tenant_id: Mapped[str] = mapped_column(
        ForeignKey("tenants.id"),
        index=True
    )

    patient_id: Mapped[str] = mapped_column(
        ForeignKey("patients.id"),
        index=True
    )

    document_id: Mapped[str] = mapped_column(
        ForeignKey("clinical_documents.id"),
        index=True
    )

    biomarker: Mapped[str] = mapped_column(
        String(120),
        index=True
    )

    value: Mapped[float] = mapped_column(
        Float
    )

    unit: Mapped[str] = mapped_column(
        String(40),
        default=""
    )

    reference_range: Mapped[str | None] = mapped_column(
        String(80),
        nullable=True
    )

    source_page: Mapped[int | None] = mapped_column(
        nullable=True
    )

    confidence: Mapped[float] = mapped_column(
        Float,
        default=0.5
    )

    review_status: Mapped[str] = mapped_column(
        String(30),
        default="PENDING_REVIEW"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=current_time
    )

    document: Mapped[ClinicalDocument] = relationship(
        back_populates="observations"
    )


class AuditLog(Base):

    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=generate_id
    )

    tenant_id: Mapped[str] = mapped_column(
        ForeignKey("tenants.id"),
        index=True
    )

    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id")
    )

    action: Mapped[str] = mapped_column(
        String(100)
    )

    resource_type: Mapped[str] = mapped_column(
        String(80)
    )

    resource_id: Mapped[str | None] = mapped_column(
        String(36),
        nullable=True
    )

    details: Mapped[dict] = mapped_column(
        JSON,
        default=dict
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=current_time
    )