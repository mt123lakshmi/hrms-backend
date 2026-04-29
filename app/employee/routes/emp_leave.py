# app/employee/routes/leave.py

from fastapi import APIRouter, Depends, HTTPException
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


# =========================================================
# 🔹 GET ALL LEAVES
# =========================================================
@router.get("/")
async def get_leaves(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(employee_required)
):
    try:
        return await get_employee_leaves(db, current_user)

    except HTTPException as e:
        # 🔥 preserve known errors
        raise e

    except Exception as e:
        # 🔥 debug log
        print("GET LEAVES ERROR:", str(e))

        raise HTTPException(
            status_code=500,
            detail="Failed to fetch leave data"
        )


# =========================================================
# 🔹 CREATE LEAVE REQUEST
# =========================================================
@router.post("/")
async def request_leave(
    payload: CreateLeaveRequest,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(employee_required)
):
    try:
        return await create_leave_request(db, current_user, payload)

    except HTTPException as e:
        # 🔥 preserve validation errors
        raise e

    except Exception as e:
        # 🔥 debug log
        print("CREATE LEAVE ERROR:", str(e))

        raise HTTPException(
            status_code=500,
            detail="Failed to create leave request"
        )