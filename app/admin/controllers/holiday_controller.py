from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.holiday import Holiday
from app.schemas.admin.holiday_schema import HolidayCreate


async def create_holiday(db: AsyncSession, data: HolidayCreate):

    result = await db.execute(
        select(Holiday).where(
            Holiday.date == data.date,
            Holiday.name == data.name
        )
    )
    existing = result.scalar_one_or_none()

    if existing:
        raise HTTPException(status_code=400, detail="Holiday already exists")

    holiday = Holiday(
        date=data.date,
        name=data.name,
        type=data.type,
        description=data.description
    )

    db.add(holiday)
    await db.commit()
    await db.refresh(holiday)

    return holiday


async def get_all_holidays(db: AsyncSession):

    result = await db.execute(
        select(Holiday).order_by(Holiday.date.asc())
    )

    return result.scalars().all()


async def delete_holiday(db: AsyncSession, holiday_id: int):

    result = await db.execute(
        select(Holiday).where(Holiday.id == holiday_id)
    )
    holiday = result.scalar_one_or_none()

    if not holiday:
        raise HTTPException(status_code=404, detail="Holiday not found")

    await db.delete(holiday)
    await db.commit()

    return {"message": "Deleted successfully"}