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
    TimeSheetHistoryResponse,
    TimeSheetActionRequest
)

# ✅ IMPORT ADMIN DEPENDENCY
from app.core.dependencies import admin_required


# ✅ APPLY ADMIN ACCESS GLOBALLY (BEST PRACTICE)
router = APIRouter(
    prefix="/timesheet",
    tags=["Timesheet"],
    dependencies=[Depends(admin_required)]   # 🔥 THIS IS THE FIX
)


# ✅ LIST VIEW (ALL EMPLOYEES)
@router.get("/latest", response_model=List[LatestTimeSheetResponse])
async def latest_timesheets(db: AsyncSession = Depends(get_db)):
    return await get_latest_timesheets(db)


# ✅ DETAIL VIEW (SINGLE EMPLOYEE)
@router.get("/latest/{employee_id}", response_model=LatestTimeSheetResponse)
async def latest_single(employee_id: int, db: AsyncSession = Depends(get_db)):
    return await get_latest_timesheet_by_employee(db, employee_id)


# ✅ HISTORY
@router.get("/history/{employee_id}", response_model=List[TimeSheetHistoryResponse])
async def history(employee_id: int, db: AsyncSession = Depends(get_db)):
    return await get_employee_history(db, employee_id)


# ✅ ACTION (APPROVE / REJECT)
@router.put("/action/{timesheet_id}")
async def action(
    timesheet_id: int,
    request: TimeSheetActionRequest,
    db: AsyncSession = Depends(get_db)
):
    return await timesheet_action(
        db,
        timesheet_id,
        request.action,
        request.reason
    )