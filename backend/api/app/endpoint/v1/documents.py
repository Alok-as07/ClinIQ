import asyncio
import logging
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, status,UploadFile, File
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.session import get_db
from app.endpoint.deps import get_current_user
from app.core.config import settings
from app.models.entities import Patient,ClinicalDocument,Observation,AuditLog

from app.schemas.contracts import  DocumentResponse


from ai_engine.ingestion.pdf import extract_pdf_pages
from ai_engine.privacy.redactor import redact_text
from ai_engine.extraction.labs import extract_lab_observations
from ai_engine.storage.encrypted_files import save_encrypted_file


router = APIRouter(
    prefix="/documents",
    tags=["Documents"]
)
logger = logging.getLogger(__name__)

@router.post("/{patient_id}", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    patient_id: int,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    #verify patient and tenant
    result = await db.execute(
        select(Patient).where(Patient.id == patient_id, Patient.tenant_id == current_user.tenant_id)
    )

    patient = result.scalar_one_or_none()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )

    if not file or not file.filename or  Path(file.filename).suffix.lower() != ".pdf":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file. Only PDF files are accepted."
        )

    content = await file.read()
    if not content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Empty file uploaded."
        )

    max_file_size = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if len(content) > max_file_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File size exceeds the maximum limit of {settings.MAX_UPLOAD_SIZE_MB} MB."
        )

    if not content.startswith(b"%PDF"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is not a valid PDF."
        )

    encrypted_path = None

    try:
        pages = await asyncio.to_thread(extract_pdf_pages, content)

        raw_text = "\n".join(
            page["text"]
            for page in pages
        )

        if not raw_text.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No extractable text found. OCR support is required for scanned PDFs."
            )

        # Redact sensitive information
        redacted_text,redaction_counts = redact_text(raw_text)

        # Encrypt and store original PDF
        encrypted_path = await asyncio.to_thread(
            save_encrypted_file,
            content,
            Path(file.filename).name,
        )

        # Extract lab values from PDF
        observations = extract_lab_observations(pages)

        # Create document record
        document = ClinicalDocument(
            tenant_id=current_user.tenant_id,
            patient_id=patient.id,
            uploaded_by=current_user.id,
            filename=file.filename,
            encrypted_path=encrypted_path,
            document_type="LAB_REPORT",
            processing_status="PROCESSED",
            redacted_text=redacted_text
        )
        db.add(document)

        await db.flush()  # Ensure document.id is available

        # Save extracted observations
        for item in observations:
            observation = Observation(
                tenant_id=current_user.tenant_id,
                patient_id=patient.id,
                document_id=document.id,
                biomarker=item["biomarker"],
                value=item["value"],
                unit=item["unit"],
                reference_range=item.get("reference_range"),
                source_page=item["source_page"],
                confidence=item["confidence"],
                review_status="PENDING_REVIEW",
            )
            db.add(observation)

        # Audit log
        db.add(
            AuditLog(
                tenant_id=current_user.tenant_id,
                user_id=current_user.id,
                action="DOCUMENT_UPLOADED",
                resource_type="CLINICAL_DOCUMENT",
                resource_id=document.id,
                details={
                    "observation_count": len(observations),
                    "redaction_counts": redaction_counts,
                },
            )
        )

        await db.commit()

        #  Index redacted text in vector database
        try:
            from ai_engine.rag.service import index_document_chunks

            await asyncio.to_thread(
                index_document_chunks,
                current_user.tenant_id,
                patient.id,
                document.id,
                redacted_text
            )
        except ModuleNotFoundError as e:
            logger.info("Document indexing is unavailable: %s", e)
        except Exception as e:
            logger.error(f"Failed to index document {document.id} in vector database: {e}")

        return DocumentResponse(
            id=document.id,
            filename=document.filename,
            document_type=document.document_type,
            processing_status=document.processing_status,
            created_at=document.created_at,
            observations=[
                {
                    "id": "",
                    **item,
                    "review_status": "PENDING_REVIEW",
                }
                for item in observations
            ],
        )

    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        logger.exception("Document upload failed")
        if encrypted_path:
            try:
                Path(encrypted_path).unlink(missing_ok=True)
            except OSError:
                logger.exception("Failed to clean up encrypted upload")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing the document."
        ) from e


@router.get("/{patient_id}/documents", response_model=DocumentResponse)
async def list_patient_documents(
    patient_id:str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    patient_result = await db.execute(
        select(Patient).where(Patient.id == patient_id, Patient.tenant_id == current_user.tenant_id
        )
    )

    if not patient_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )

    result = await db.execute(
        select(ClinicalDocument)
        .option(selectinload(ClinicalDocument.observations))
        .where(
            ClinicalDocument.patient_id == patient_id,
            ClinicalDocument.tenant_id == current_user.tenant_id
        )
        .order_by(ClinicalDocument.created_at.desc())
    )

    return result.scalars().unique().all()
