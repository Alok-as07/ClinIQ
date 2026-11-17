from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.endpoint.deps import get_current_user
from app.models.entities import Patient

from app.schemas.contracts import (
    PatientCreate,
    PatientUpdate,
    PatientResponse,
)

router = APIRouter(
    prefix="/patients",
    tags=["Patients"]
)

@router.post("", response_model=PatientResponse, status_code=status.HTTP_201_CREATED)
async def create_patient(requestBody: PatientCreate, db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    patient = Patient(
        tenant_id=current_user.tenant_id,
        **requestBody.model_dump()
    )
    db.add(patient)
    await db.commit()
    await db.refresh(patient)
    return patient

@router.get("", response_model=list[PatientResponse])
async def list_patients(
    search: str | None = None,
    skip: int = 0,
    limit: int = 25,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    if skip <0 or limit<1 or limit>100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid pagination parameters"
        )
    query = select(Patient).where(Patient.tenant_id == current_user.tenant_id)

    if search:
        search_pattern = f"%{search}%"
        query = query.where(Patient.display_name.ilike(search_pattern))

    query = (
        query
        .order_by(Patient.created_at.desc())
        .offset(skip)
        .limit(limit)
    )

    result = await db.execute(query)
    patients = result.scalars().all()
    return patients

@router.get("/{patient_id}", response_model=PatientResponse)
async def get_patient(patient_id: str, db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    query = select(Patient).where(Patient.id == patient_id, Patient.tenant_id == current_user.tenant_id)
    result = await db.execute(query)
    patient = result.scalar_one_or_none()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    return patient

@router.patch("/{patient_id}", response_model=PatientResponse)
async def update_patient(patient_id: str, requestBody: PatientUpdate, db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    query = select(Patient).where(Patient.id == patient_id, Patient.tenant_id == current_user.tenant_id)
    result = await db.execute(query)
    patient = result.scalar_one_or_none()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    for field, value in requestBody.model_dump(exclude_unset=True).items():
        setattr(patient, field, value)
    await db.commit()
    await db.refresh(patient)
    return patient