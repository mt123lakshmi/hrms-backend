# app/admin/routes/timesheet.py

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.database.database import get_db
from app.admin.controllers.timesheet_controller import (
    get_latest_timesheets,
    get_latest_timesheet_by_employee,
    get_employee_history,
    timesheet_action
)

from app.schemas.admin.timesheet_schema import (
    LatestTimeSheetResponse,
    TimeSheetHistoryGroupedResponse,   # 🔥 FIXED
    TimeSheetActionRequest
)

from app.core.dependencies import admin_required


router = APIRouter(
    prefix="/timesheet",
    tags=["Timesheet"]
)


# =========================================================
# ✅ LIST VIEW (ALL EMPLOYEES) → NO CHANGE
# =========================================================
@router.get("/latest", response_model=List[LatestTimeSheetResponse])
async def latest_timesheets(
    db: AsyncSession = Depends(get_db),
    user=Depends(admin_required)
):
    return await get_latest_timesheets(db, user)


# =========================================================
# ✅ DETAIL VIEW (SINGLE EMPLOYEE) → NO CHANGE
# =========================================================
@router.get("/latest/{employee_id}", response_model=LatestTimeSheetResponse)
async def latest_single(
    employee_id: int,
    db: AsyncSession = Depends(get_db),
    user=Depends(admin_required)
):
    return await get_latest_timesheet_by_employee(db, employee_id, user)


# =========================================================
# 🔥 HISTORY (FIXED — GROUPED RESPONSE)
# =========================================================
@router.get("/history/{employee_id}", response_model=TimeSheetHistoryGroupedResponse)
async def history(
    employee_id: int,
    db: AsyncSession = Depends(get_db),
    user=Depends(admin_required)
):
    return await get_employee_history(db, employee_id, user)


# =========================================================
# ✅ ACTION (NO CHANGE)
# =========================================================
@router.put("/action/{timesheet_id}")
async def action(
    timesheet_id: int,
    request: TimeSheetActionRequest,
    db: AsyncSession = Depends(get_db),
    user=Depends(admin_required)
):
    return await timesheet_action(
        db,
        timesheet_id,
        request.action,
        request.reason,
        user=user
    )