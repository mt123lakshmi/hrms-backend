from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.database import get_db

from app.schemas.auth.forgot_password import (
    ForgotPasswordRequest,
    ResetPasswordRequest
)

from app.auth.controllers.password_controller import (
    send_otp,
    reset_password
)

router = APIRouter(prefix="/auth", tags=["Forgot Password"])


# 🔥 Send OTP
@router.post("/forgot-password")
async def forgot_password_api(
    data: ForgotPasswordRequest,
    db: AsyncSession = Depends(get_db)
):
    return await send_otp(db, data.email)


# 🔥 Reset Password
@router.post("/reset-password")
async def reset_password_api(
    data: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db)
):
    return await reset_password(
        db,
        data.email,
        data.otp,
        data.new_password,
        data.confirm_password
    )