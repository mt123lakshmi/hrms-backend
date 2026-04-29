from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import traceback

from app.core.security import decode_access_token
from app.database.database import get_db
from app.models.user import User

security = HTTPBearer()


# ===============================
# 🔹 COMMON FUNCTION (FULL SAFE VERSION)
# ===============================
async def get_user_from_token(token: str, db: AsyncSession):
    try:
        # ✅ Decode token safely
        payload = decode_access_token(token)

        if not payload:
            raise HTTPException(status_code=401, detail="Invalid token")

        user_id = payload.get("user_id")
        role = payload.get("role")

        if not user_id or not role:
            raise HTTPException(status_code=401, detail="Invalid token payload")

        role = role.lower()

        # ✅ Fetch user safely
        result = await db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(status_code=401, detail="User not found")

        return user, role

    except HTTPException:
        # pass through known errors
        raise

    except Exception:
        # 🔥 THIS IS WHAT YOU WERE MISSING
        print("🔥 AUTH ERROR TRACE:")
        print(traceback.format_exc())

        raise HTTPException(
            status_code=500,
            detail="Authentication failed"
        )


# ===============================
# 🔹 ADMIN ONLY
# ===============================
async def admin_required(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    if not credentials or not credentials.credentials:
        raise HTTPException(status_code=401, detail="Authorization required")

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
    if not credentials or not credentials.credentials:
        raise HTTPException(status_code=401, detail="Authorization required")

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
    if not credentials or not credentials.credentials:
        raise HTTPException(status_code=401, detail="Authorization required")

    token = credentials.credentials

    user, role = await get_user_from_token(token, db)

    if role not in ["admin", "employee"]:
        raise HTTPException(status_code=403, detail="Access denied")

    return user