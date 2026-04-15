from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database import get_db
from app.core.dependencies import employee_required
from app.employee.controllers.emp_leave_controller import (
    get_employee_leaves,
    create_leave_request
)
from app.schemas.employee.leave_schema import CreateLeaveRequest

router = APIRouter(
    prefix="/employee/leave",
    tags=["Employee Leave"]
)


# 🔹 GET ALL LEAVES
@router.get("/")
async def get_leaves(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(employee_required)
):
    return await get_employee_leaves(db, current_user)


# 🔹 CREATE LEAVE
@router.post("/")
async def request_leave(
    payload: CreateLeaveRequest,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(employee_required)
):
    return await create_leave_request(db, current_user, payload)