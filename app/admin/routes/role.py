# app/admin/routes/role.py

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database import get_db
from app.core.dependencies import admin_required
from app.admin.controllers.role_controller import get_roles_controller

router = APIRouter(prefix="/roles", tags=["Roles"])


@router.get("/")
async def get_roles(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(admin_required)   # 🔥 admin only
):
    return await get_roles_controller(db)