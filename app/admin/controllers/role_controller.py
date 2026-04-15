# app/admin/controllers/role_controller.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.role import Role

async def get_roles_controller(db: AsyncSession):

    result = await db.execute(select(Role))
    roles = result.scalars().all()

    return {
        "success": True,
        "data": [
            {
                "id": r.id,
                "name": r.name
            }
            for r in roles
        ]
    }