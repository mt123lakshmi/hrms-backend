from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from datetime import datetime
 
from app.models.employee_asset import EmployeeAsset
 
 
# ===============================
# 🔹 GET ASSETS (TABLE)
# ===============================
async def get_assets_controller(db: AsyncSession):
 
    result = await db.execute(
        select(EmployeeAsset).options(
            selectinload(EmployeeAsset.employee)
        )
    )
 
    assets = result.scalars().all()
 
    data = []
 
    for a in assets:
        data.append({
            "asset_id": a.id,   # ✅ FIXED
            "employee_id": a.employee.id if a.employee else None,
            "employee_name": a.employee.name if a.employee else None,
            "laptop_asset_id": a.laptop_asset_id,
            "access_card": a.access_card,
            "additional_asset": a.additional_asset,
            "status": a.status,
 
            "unassign_reason": a.return_reason if a.status == "unassigned" else None
        })
 
    return {"success": True, "data": data}
 
 
# ===============================
# 🔹 ASSIGN / UNASSIGN
# ===============================
async def asset_action_controller(asset_id: int, data, db: AsyncSession):
 
    result = await db.execute(
        select(EmployeeAsset).where(EmployeeAsset.id == asset_id)
    )
    asset = result.scalar_one_or_none()
 
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
 
    # ===============================
    # ASSIGN
    # ===============================
    if data.action == "assign":
 
        if asset.status == "assigned":
            return {
                "success": False,
                "message": "Asset already assigned"
            }
 
        asset.status = "assigned"
        asset.assigned_reason = data.reason
        asset.assigned_at = datetime.utcnow()
 
    # ===============================
    # UNASSIGN
    # ===============================
    elif data.action == "unassign":
 
        if asset.status == "unassigned":
            return {
                "success": False,
                "message": "Asset already unassigned"
            }
 
        asset.status = "unassigned"
        asset.return_reason = data.reason
        asset.returned_at = datetime.utcnow()
 
    # commit changes
    await db.commit()
 
    return {
        "success": True,
        "message": f"Asset {data.action} successful"
    }