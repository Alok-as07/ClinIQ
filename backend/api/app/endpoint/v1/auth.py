from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.models.entities import User,Tenant
from app.schemas.contracts import ( RegisterRequest, LoginRequest, TokenResponse)
from app.core.security import ( hash_password, verify_password, create_access_token)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(requestBody: RegisterRequest, db: AsyncSession = Depends(get_db)):
    email = requestBody.email.lowe()

    result = await db.execute(
        select(User).where(User.email == email)
    )
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    try:
        tenant = Tenant(name=requestBody.tenant_name)
        db.add(tenant)
        await db.flush()  # Ensure tenant.id is available
        user = User(
            tenant_id=tenant.id,
            full_name=requestBody.full_name,
            email=email,
            password_hash=hash_password(requestBody.password),
            role=requestBody.role | "TENANT_ADMIN"
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        token = create_access_token(user_id=user.id, tenant_id=tenant.id)

        return TokenResponse(
            access_token=token,
            # token_type="bearer",
            user_id=user.id,
            tenant_id=tenant.id
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during registration"
        ) from e

@router.post('/login',response_model=TokenResponse)
async def login(requestBody: LoginRequest, db: AsyncSession = Depends(get_db)):
    email = requestBody.email.lower()

    result = await db.execute(
        select(User).where(User.email == email)
    )
    user = result.scalar_one_or_none()

    if( not user or not verify_password(requestBody.password,user.password_hash) or not user.is_active):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    token = create_access_token(user_id=user.id, tenant_id=user.tenant_id)
    return TokenResponse(
        access_token=token,
        # token_type="bearer",
        user_id=user.id,
        tenant_id=user.tenant_id
    )