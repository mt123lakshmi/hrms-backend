# app/employee/routes/payslip.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database import get_db
from app.core.dependencies import employee_required
from app.employee.controllers.emppayslip_controller import get_my_payslips


router = APIRouter(
    prefix="/employee/payslips",
    tags=["Employee Payslips"]
)


# ===============================
# 🔹 GET MY PAYSLIPS
# ===============================
@router.get("/")
async def get_my_payslips_route(
    db: AsyncSession = Depends(get_db),
    user = Depends(employee_required)
):
    try:
        return await get_my_payslips(db, user)

    except HTTPException as e:
        raise e

    except Exception as e:
        print("PAYSLIP ERROR:", str(e))

        raise HTTPException(
            status_code=500,
            detail="Failed to fetch payslips"
        )