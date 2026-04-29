from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database import get_db
from app.core.dependencies import admin_required

from app.schemas.admin.task_schema import TaskCreate

from app.admin.controllers.tasktimesheet_controller import (
    get_all_employees,
    get_task_dashboard,
    assign_task,
    approve_worklog,
    reject_worklog
)

router = APIRouter(prefix="/admin", tags=["Admin Task Timesheet"])


# =========================================================
# 1. GET ALL EMPLOYEES
# =========================================================
@router.get("/employees")
async def employees(
    db: AsyncSession = Depends(get_db),
    user=Depends(admin_required)
):
    return await get_all_employees(db, user)   # 🔥 FIX


# =========================================================
# 2. EMPLOYEE DASHBOARD
# =========================================================
@router.get("/employee-dashboard/{emp_id}")
async def dashboard(
    emp_id: int,
    db: AsyncSession = Depends(get_db),
    user=Depends(admin_required)
):
    return await get_task_dashboard(emp_id, db, user)   # 🔥 FIX


# =========================================================
# 3. ASSIGN TASK
# =========================================================
@router.post("/assign-task")
async def assign(
    data: TaskCreate,
    db: AsyncSession = Depends(get_db),
    user=Depends(admin_required)
):
    return await assign_task(data, db, user)   # 🔥 FIX


# =========================================================
# 4. APPROVE WORKLOG
# =========================================================
@router.post("/worklog/{log_id}/approve")
async def approve(
    log_id: int,
    db: AsyncSession = Depends(get_db),
    user=Depends(admin_required)
):
    return await approve_worklog(log_id, db, user)   # 🔥 FIX


# =========================================================
# 5. REJECT WORKLOG
# =========================================================
@router.post("/worklog/{log_id}/reject")
async def reject(
    log_id: int,
    reason: str,
    db: AsyncSession = Depends(get_db),
    user=Depends(admin_required)
):
    return await reject_worklog(log_id, reason, db, user)   # 🔥 FIX