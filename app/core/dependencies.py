from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.security import SECRET_KEY, ALGORITHM, decode_access_token
from app.database.database import get_db
from app.models.user import User
from app.core.security import decode_access_token
security = HTTPBearer()


# ===============================
# 🔹 GET CURRENT USER (DB ONLY FOR USER DATA)
# ===============================
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    if credentials is None:
        raise HTTPException(401, "Not authenticated")

    token = credentials.credentials

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")

        if not user_id:
            raise HTTPException(401, "Invalid token")

        # 🔥 ONLY fetch user (NO role dependency)
        result = await db.execute(
            select(User).where(User.id == user_id)
        )

        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(401, "User not found")

        return user

    except JWTError:
        raise HTTPException(401, "Invalid token")


# ===============================
# 🔹 ADMIN REQUIRED (TOKEN-BASED)
# ===============================
async def admin_required(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    token = credentials.credentials
    payload = decode_access_token(token)

    print("TOKEN PAYLOAD:", payload)  # debug

    if not payload:
        raise HTTPException(401, "Invalid token")

    if payload.get("role") != "admin":
        raise HTTPException(403, "Admin access only")

    # ✅ FETCH USER (IMPORTANT)
    result = await db.execute(
        select(User).where(User.id == payload.get("user_id"))
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(401, "User not found")

    return user   # ✅ RETURN USER OBJECT
# ===============================
# 🔹 EMPLOYEE REQUIRED (TOKEN-BASED)
# ===============================
async def employee_required(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    token = credentials.credentials
    payload = decode_access_token(token)

    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    role = payload.get("role")

    if not role or role.lower() != "employee":
        raise HTTPException(status_code=403, detail="Employee only")

    result = await db.execute(
        select(User).where(User.id == payload.get("user_id"))
    )
    user = result.scalar_one_or_none()

    return user
# ===============================
# 🔹 ADMIN OR EMPLOYEE (TOKEN-BASED)
# ===============================
async def admin_or_employee(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    token = credentials.credentials
    payload = decode_access_token(token)

    if not payload:
        raise HTTPException(401, "Invalid token")

    if payload.get("role") not in ["admin", "employee"]:
        raise HTTPException(403, "Access denied")

    result = await db.execute(
        select(User).where(User.id == payload.get("user_id"))
    )
    user = result.scalar_one_or_none()

    return user