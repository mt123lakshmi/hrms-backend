# app/admin/routes/asset.py

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database import get_db
from app.core.dependencies import admin_required

from app.schemas.admin.asset_schema import AssetActionRequest
from app.admin.controllers.asset_controller import (
    get_assets_controller,
    asset_action_controller,
    download_assets_excel_controller
)

router = APIRouter(
    prefix="/admin/assets",
    tags=["Assets Management"]
)


# 🔹 GET TABLE
@router.get("/")
async def get_assets(
    db: AsyncSession = Depends(get_db),
    user=Depends(admin_required)
):
    return await get_assets_controller(db, user)   # 🔥 FIX


# 🔹 ACTION (ASSIGN / UNASSIGN)
@router.post("/{asset_id}/action")
async def asset_action(
    asset_id: int,
    data: AssetActionRequest,
    db: AsyncSession = Depends(get_db),
    user=Depends(admin_required)
):
    return await asset_action_controller(asset_id, data, db, user)   # 🔥 FIX


# 🔹 DOWNLOAD
@router.get("/download")
async def download_assets(
    db: AsyncSession = Depends(get_db),
    user=Depends(admin_required)
):
    return await download_assets_excel_controller(db, user)   # 🔥 FIX