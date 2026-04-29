# app/employee/routes/profile.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database import get_db
from app.core.dependencies import employee_required

from app.employee.controllers.profile_controller import (
    get_employee_profile_controller,
    update_profile,
    change_password
)

from app.schemas.employee.employee_schema import (
    UpdateProfileRequest,
    ChangePasswordRequest
)


router = APIRouter(
    prefix="/employee",
    tags=["Employee Profile"]
)


# =========================================================
# 🔹 GET PROFILE
# =========================================================
@router.get("/profile")
async def get_profile(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(employee_required)
):
    try:
        return await get_employee_profile_controller(db, current_user)

    except HTTPException as e:
        raise e

    except Exception as e:
        print("PROFILE ERROR:", str(e))
        raise HTTPException(status_code=500, detail="Failed to fetch profile")


# =========================================================
# 🔹 UPDATE PROFILE
# =========================================================
@router.patch("/profile")
async def update_profile_route(
    data: UpdateProfileRequest,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(employee_required)
):
    try:
        return await update_profile(db, current_user, data)

    except HTTPException as e:
        raise e

    except Exception as e:
        print("UPDATE PROFILE ERROR:", str(e))
        raise HTTPException(status_code=500, detail="Failed to update profile")


# =========================================================
# 🔹 CHANGE PASSWORD
# =========================================================
@router.put("/change-password")
async def change_password_route(
    data: ChangePasswordRequest,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(employee_required)
):
    try:
        return await change_password(db, current_user, data)

    except HTTPException as e:
        raise e

    except Exception as e:
        print("CHANGE PASSWORD ERROR:", str(e))
        raise HTTPException(status_code=500, detail="Failed to change password")