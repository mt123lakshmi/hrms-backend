from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database import get_db
from app.core.dependencies import employee_required
from app.employee.controllers.profile_controller import get_employee_profile_controller,update_profile,change_password

from app.schemas.employee.employee_schema import UpdateProfileRequest, ChangePasswordRequest

router = APIRouter(
    prefix="/employee",
    tags=["Employee Profile"]
)

@router.get("/profile")
async def get_profile(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(employee_required)
):
    return await get_employee_profile_controller(db, current_user)


@router.patch("/profile")
async def update_profile_route(
    data: UpdateProfileRequest,
    db=Depends(get_db),
    current_user=Depends(employee_required)
):
    return await update_profile(db, current_user, data)

@router.put("/change-password")
async def change_password_route(
    data: ChangePasswordRequest,
    db=Depends(get_db),
    current_user=Depends(employee_required)
):
    return await change_password(db, current_user, data)