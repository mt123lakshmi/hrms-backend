 
from sqlalchemy import select
from fastapi import HTTPException
import random
from datetime import datetime, timedelta
 
from app.models.user import User
from app.core.response import success_response, error_response
from app.core.security import verify_password, create_access_token, hash_password
from app.utils.send_email import send_otp_email
 
 
MAX_OTP_ATTEMPTS = 3
 
 
# =========================================================
# 🔹 LOGIN
# =========================================================
async def login_controller(data, db):
 
    result = await db.execute(
        select(User).where(User.company_email == data.company_email)
    )
    user = result.scalar_one_or_none()
 
    if not user:
        return error_response("User not found", 404)
 
    # 🔥 password check
    if not verify_password(data.password, user.password):
        return error_response("Invalid password", 401)
 
    # 🔥 FIXED TOKEN
    token = create_access_token({
        "user_id": user.id,
        "employee_id": user.employee_id,
        "company_id": user.company_id,     # 🔥 CRITICAL
        "role": user.role.name,            # 🔥 FIX
        "sub": user.company_email
    })
 
    return success_response({
        "access_token": token,
        "token_type": "bearer"
    }, "Login successful")
 