# app/admin/controllers/attendance_controller.py

from datetime import date
import calendar
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.holiday import Holiday


async def get_attendance_overview_controller(
    year: int,
    month: int,
    db: AsyncSession,
    user
):

    # ===============================
    # 🔹 GET LAST DAY OF MONTH
    # ===============================
    last_day = calendar.monthrange(year, month)[1]

    start_date = f"{year}-{month:02d}-01"
    end_date = f"{year}-{month:02d}-{last_day}"

    # ===============================
    # 🔹 FETCH HOLIDAYS
    # ===============================
    result = await db.execute(
        select(Holiday).where(
            Holiday.date.between(start_date, end_date),
            Holiday.company_id == user.company_id
        )
    )
    holidays = result.scalars().all()

    # ===============================
    # 🔥 FIX 1: NORMALIZE DATE KEYS
    # ===============================
    holiday_map = {
        h.date.strftime("%Y-%m-%d"): (h.type or "").strip().lower()
        for h in holidays
    }

    result_data = []

    # ===============================
    # 🔹 BUILD CALENDAR
    # ===============================
    for day in range(1, last_day + 1):
        current_date = date(year, month, day)
        current_date_str = current_date.strftime("%Y-%m-%d")

        # ===============================
        # 🔥 FIX 2: USE STRING MATCH
        # ===============================
        if current_date_str in holiday_map:

            holiday_type = holiday_map[current_date_str]

            # ===============================
            # 🔥 FIX 3: STANDARDIZE TYPES
            # ===============================
            if holiday_type in ["public", "public holiday"]:
                day_type = "public_holiday"

            elif holiday_type in ["festival", "festival holiday"]:
                day_type = "festival_holiday"

            else:
                day_type = "working_day"

        elif current_date.weekday() >= 5:
            day_type = "weekend"

        else:
            day_type = "working_day"

        result_data.append({
            "date": current_date_str,
            "day": day,
            "weekday": current_date.strftime("%A"),
            "type": day_type
        })

    return {
        "success": True,
        "year": year,
        "month": calendar.month_name[month],
        "data": result_data
    }