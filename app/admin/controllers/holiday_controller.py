from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.holiday import Holiday
from app.schemas.admin.holiday_schema import HolidayCreate


# ===============================
# 🔹 CREATE HOLIDAY
# ===============================
async def create_holiday(db: AsyncSession, data: HolidayCreate, user):

    # 🔥 prevent duplicate per company
    result = await db.execute(
        select(Holiday).where(
            Holiday.date == data.date,
            Holiday.name == data.name,
            Holiday.company_id == user.company_id   # ✅ IMPORTANT
        )
    )
    existing = result.scalar_one_or_none()

    if existing:
        raise HTTPException(status_code=400, detail="Holiday already exists")

    # 🔥 FIX: ADD company_id
    holiday = Holiday(
        date=data.date,
        name=data.name,
        type=data.type,
        description=data.description,
        company_id=user.company_id   # ✅ CRITICAL FIX
    )

    db.add(holiday)
    await db.commit()
    await db.refresh(holiday)

    return holiday


# ===============================
# 🔹 GET HOLIDAYS
# ===============================
async def get_all_holidays(db: AsyncSession, user):

    result = await db.execute(
        select(Holiday)
        .where(Holiday.company_id == user.company_id)  # ✅ FILTER
        .order_by(Holiday.date.asc())
    )

    return result.scalars().all()


# ===============================
# 🔹 DELETE HOLIDAY
# ===============================
async def delete_holiday(db: AsyncSession, holiday_id: int, user):

    result = await db.execute(
        select(Holiday).where(
            Holiday.id == holiday_id,
            Holiday.company_id == user.company_id   # ✅ SECURITY FIX
        )
    )
    holiday = result.scalar_one_or_none()

    if not holiday:
        raise HTTPException(status_code=404, detail="Holiday not found")

    await db.delete(holiday)
    await db.commit()

    return {"message": "Deleted successfully"}