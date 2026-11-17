from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel,EmailStr,Field,ConfigDict


# -------------------------
# Authentication
# -------------------------

class RegisterRequest(BaseModel):
    tenant_name: str = Field(min_length=2,max_length=160)
    full_name: str = Field(min_length=2,max_length=160)
    email: EmailStr
    password: str = Field(min_length=8,max_length=128)
    role: str | None = Field(default="user", max_length=30)

class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8,max_length=128)

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    tenant_id: str


# -------------------------
# Patient
# -------------------------

class PatientCreate(BaseModel):
    display_name: str = Field(min_length=2, max_length=160)
    external_ref: str | None = None
    date_of_birth: str | None = None
    sex: str | None = None

class PatientUpdate(BaseModel):
    display_name: str | None = Field(default=None, min_length=2, max_length=160)
    external_ref: str | None = None
    date_of_birth: str | None = None
    sex: str | None = None

class PatientResponse(BaseModel):
    id: str
    display_name: str
    external_ref: str | None
    date_of_birth: str | None
    sex: str | None
    created_at: datetime

    model_config = ConfigDict( from_attributes=True )

# -------------------------
# Observation
# -------------------------

class ObservationResponse(BaseModel):
    id: str
    biomarker: str
    value: float
    unit: str
    reference_range: str | None
    source_page: int | None
    confidence: float
    review_status: str

    model_config = ConfigDict(from_attributes=True)

class DocumentResponse(BaseModel):
    id: str
    filename: str
    document_type: str
    processing_status: str
    created_at: datetime
    observations: list[ObservationResponse] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)