from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database import get_db
from app.core.dependencies import employee_required

from app.admin.controllers.master_controller import (
    
  
    get_leave_types_controller,
    get_day_types_controller
)

router = APIRouter(prefix="/master", tags=["Master"])





@router.get("/leave-types")
async def get_leave_types_route(
    db: AsyncSession = Depends(get_db),
    user=Depends(employee_required)
):
    return await get_leave_types_controller(db)


@router.get("/day-types")
async def get_day_types(
    db: AsyncSession = Depends(get_db),
    user=Depends(employee_required)
):
    return await get_day_types_controller(db)