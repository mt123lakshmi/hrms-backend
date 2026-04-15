# app/admin/routes/attendance.py

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database import get_db
from app.core.dependencies import admin_required
from app.admin.controllers.attendance_controller import get_attendance_overview_controller

router = APIRouter(
    prefix="/admin/attendance",
    tags=["Attendance"]
)


@router.get("/overview")
async def attendance_overview(
    year: int,
    month: int,
    db: AsyncSession = Depends(get_db),
    user = Depends(admin_required)  # 🔥 RBAC
):
    return await get_attendance_overview_controller(year, month, db)




# "dfghjklkjhgfdsdfghjkjhgfdszxdfgh"    