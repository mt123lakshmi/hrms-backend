from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession



from app.models.leave_type import LeaveType
from app.models.day_type import DayType


async def fetch_all(db: AsyncSession, model):
    result = await db.execute(select(model))
    return result.scalars().all()




async def get_leave_types_controller(db: AsyncSession):
    data = await fetch_all(db, LeaveType)

    return {
        "success": True,
        "data": [
            {
                "id": lt.id,
                "name": lt.name,
                "max_per_quarter": lt.max_per_quarter,
                "carry_forward": lt.carry_forward
            }
            for lt in data
        ]
    }


async def get_day_types_controller(db: AsyncSession):
    data = await fetch_all(db, DayType)

    return {
        "success": True,
        "data": [{"id": d.id, "name": d.name} for d in data]
    }