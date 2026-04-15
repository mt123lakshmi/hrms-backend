# app/admin/routes/holiday.py

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.database.database import get_db
from app.schemas.admin.holiday_schema import HolidayCreate, HolidayResponse
from app.admin.controllers import holiday_controller

# 🔥 RBAC IMPORTS
from app.core.dependencies import admin_required, admin_or_employee

router = APIRouter(prefix="/holidays", tags=["Holiday Management"])


# ===============================
# 🔹 CREATE HOLIDAY (ADMIN ONLY)
# ===============================
@router.post("/", response_model=HolidayResponse)
async def add_holiday(
    data: HolidayCreate,
    db: AsyncSession = Depends(get_db),
    user = Depends(admin_required)  # 🔥 ADMIN ONLY
):
    return await holiday_controller.create_holiday(db, data)


# ===============================
# 🔹 GET HOLIDAYS (ADMIN + EMPLOYEE)
# ===============================
@router.get("/", response_model=List[HolidayResponse])
async def get_holidays(
    db: AsyncSession = Depends(get_db),
    user = Depends(admin_or_employee)  # 🔥 BOTH ALLOWED
):
    return await holiday_controller.get_all_holidays(db)


# ===============================
# 🔹 DELETE HOLIDAY (ADMIN ONLY)
# ===============================
@router.delete("/{holiday_id}")
async def delete_holiday(
    holiday_id: int,
    db: AsyncSession = Depends(get_db),
    user = Depends(admin_required)  # 🔥 ADMIN ONLY
):
    return await holiday_controller.delete_holiday(db, holiday_id)