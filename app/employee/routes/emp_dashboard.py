from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database import get_db
from app.core.dependencies import employee_required
from app.employee.controllers.dashboard_controller import get_employee_dashboard
from app.schemas.employee.dashboard_schema import DashboardResponse


router = APIRouter(
    prefix="/employee",
    tags=["Employee Dashboard"]
)


@router.get("/dashboard", response_model=DashboardResponse)
async def employee_dashboard(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(employee_required)
):
    try:
        return await get_employee_dashboard(db, current_user)

    # ✅ let proper HTTP errors pass through
    except HTTPException as e:
        raise e

    # ✅ handle unexpected errors properly
    except Exception as e:
        print("EMPLOYEE DASHBOARD ERROR:", str(e))  # 🔥 debugging

        raise HTTPException(
            status_code=500,
            detail="Failed to fetch dashboard"
        )