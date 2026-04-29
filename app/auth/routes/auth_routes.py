from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.schemas.auth.auth_schema import LoginRequest
from app.database.database import get_db
from app.models.user import User
from app.core.security import verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login")
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):

    result = await db.execute(
        select(User)
        .options(selectinload(User.role))   # ✅ IMPORTANT
        .where(User.company_email == data.company_email)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(404, "User not found")

    if not verify_password(data.password, user.password):
        raise HTTPException(401, "Invalid password")

   
    token = create_access_token(
        {
            "user_id": user.id,
            "company_id": user.company_id,
            "role": user.role.name if user.role else None,
            "sub": user.company_email,
        }
    )

    return {
        "access_token": token,
        "token_type": "bearer",
        "role": user.role.name if user.role else None,  
    }