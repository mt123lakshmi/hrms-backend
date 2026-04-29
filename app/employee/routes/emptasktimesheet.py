# app/employee/routes/tasktimesheet.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database import get_db
from app.core.dependencies import employee_required

from app.employee.controllers.tasktimesheet_controller import (
    create_worklog,
    get_my_tasks,
    get_my_history
)

from app.schemas.employee.worklog_schema import WorkLogCreate


router = APIRouter(
    prefix="/employee",
    tags=["Employee Task Timesheet"]
)


# ==========================
# GET TASKS
# ==========================
@router.get("/tasks")
async def my_tasks(
    db: AsyncSession = Depends(get_db),
    user = Depends(employee_required)
):
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    if not user.employee_id:
        raise HTTPException(status_code=400, detail="Employee not linked")

    return await get_my_tasks(
        user.employee_id,
        db,
        user   # 🔥 CRITICAL FIX
    )


# ==========================
# CREATE WORKLOG
# ==========================
@router.post("/worklog")
async def log_progress(
    data: WorkLogCreate,
    db: AsyncSession = Depends(get_db),
    user = Depends(employee_required)
):
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    if not user.employee_id:
        raise HTTPException(status_code=400, detail="Employee not linked")

    return await create_worklog(
        user.employee_id,
        data,
        db,
        user   # 🔥 CRITICAL FIX
    )


# ==========================
# HISTORY
# ==========================
@router.get("/worklog/history")
async def my_history(
    db: AsyncSession = Depends(get_db),
    user = Depends(employee_required)
):
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    if not user.employee_id:
        raise HTTPException(status_code=400, detail="Employee not linked")

    return await get_my_history(
        user.employee_id,
        db,
        user   # 🔥 CRITICAL FIX
    )