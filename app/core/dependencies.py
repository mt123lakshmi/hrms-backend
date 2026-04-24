from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.security import decode_access_token
from app.database.database import get_db
from app.models.user import User

security = HTTPBearer()


# ===============================
# 🔹 COMMON FUNCTION (REUSE THIS)
# ===============================
async def get_user_from_token(token: str, db: AsyncSession):
    payload = decode_access_token(token)

    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    user_id = payload.get("user_id")
    role = payload.get("role", "").lower()   # 🔥 NORMALIZED HERE

    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")

    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user, role


# ===============================
# 🔹 ADMIN ONLY
# ===============================
async def admin_required(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    token = credentials.credentials

    user, role = await get_user_from_token(token, db)

    if role != "admin":
        raise HTTPException(status_code=403, detail="Admin access only")

    return user


# ===============================
# 🔹 EMPLOYEE ONLY
# ===============================
async def employee_required(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    token = credentials.credentials

    user, role = await get_user_from_token(token, db)

    if role != "employee":
        raise HTTPException(status_code=403, detail="Employee only")

    return user


# ===============================
# 🔹 ADMIN OR EMPLOYEE
# ===============================
async def admin_or_employee(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    token = credentials.credentials

    user, role = await get_user_from_token(token, db)

    if role not in ["admin", "employee"]:
        raise HTTPException(status_code=403, detail="Access denied")

    return user