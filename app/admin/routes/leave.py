from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database import get_db
from app.core.dependencies import admin_required
from app.schemas.admin.leave_schema import LeaveActionRequest

from app.admin.controllers.leave_controller import (
    get_leave_list_controller,
    get_leave_insights,
    leave_action_controller
)

router = APIRouter(prefix="/admin/leaves", tags=["Leave Management"])


# 🔹 GET ALL LEAVES
@router.get("/")
async def get_leaves(
    db: AsyncSession = Depends(get_db),
    user = Depends(admin_required)
):
    return await get_leave_list_controller(db)


# 🔹 GET INSIGHTS
@router.get("/{employee_id}/insights")
async def get_insights(
    employee_id: int,
    db: AsyncSession = Depends(get_db),
    user = Depends(admin_required)
):
    return await get_leave_insights(employee_id, db)


# 🔹 APPROVE / REJECT
@router.post("/{leave_id}/action")
async def leave_action(
    leave_id: int,
    payload: LeaveActionRequest,
    db: AsyncSession = Depends(get_db),
    user = Depends(admin_required)
):
    return await leave_action_controller(
        leave_id=leave_id,
        action=payload.action,
        reason=payload.rejection_reason,
        admin_id=user.id,
        db=db
    )