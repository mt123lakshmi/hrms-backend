# app/employee/routes/attendance.py

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database import get_db
from app.core.dependencies import employee_required   # 🔥 FIX

from app.employee.controllers.emp_attendance_controller import get_attendance_calendar


router = APIRouter(
    prefix="/attendance",
    tags=["Attendance"]
)


@router.get("/calendar")
async def attendance_calendar(
    year: int = Query(...),
    month: int = Query(...),
    db: AsyncSession = Depends(get_db),
    user = Depends(employee_required)   # 🔥 FIX
):
    return await get_attendance_calendar(year, month, db, user)