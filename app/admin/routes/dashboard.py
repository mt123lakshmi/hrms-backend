# app/admin/routes/dashboard.py

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database import get_db
from app.core.dependencies import admin_required
from app.admin.controllers import dashboard_controller

router = APIRouter(
    prefix="/admin",
    tags=["Admin Dashboard"]
)


@router.get("/dashboard")
async def get_dashboard(
    db: AsyncSession = Depends(get_db),
    user=Depends(admin_required)
):
    # 🔥 pass user (important)
    return await dashboard_controller.get_dashboard_controller(db, user)