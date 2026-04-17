from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from fastapi import HTTPException
from app.database.database import get_db
from app.schemas.employee.timesheet_schema import (
    TimeSheetCreate,
    TimeSheetResponse
)
from app.employee.controllers.emp_timesheet_controller import (
    upsert_timesheet,
    get_employee_timesheets
)
from app.core.dependencies import employee_required
router = APIRouter(prefix="/employee/timesheet", tags=["Employee Timesheet"])

@router.post("/")
async def save_timesheet(
    data: TimeSheetCreate,
    db: AsyncSession = Depends(get_db),
    user = Depends(employee_required)
):
    # 🔴 SAFETY CHECK
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    if not user.employee_id:
        raise HTTPException(status_code=400, detail="Employee not linked")

    return await upsert_timesheet(db, user.employee_id, data)


@router.get("/", response_model=List[TimeSheetResponse])
async def get_timesheets(
    db: AsyncSession = Depends(get_db),
    user = Depends(employee_required)
):
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    if not user.employee_id:
        raise HTTPException(status_code=400, detail="Employee not linked")

    return await get_employee_timesheets(db, user.employee_id)