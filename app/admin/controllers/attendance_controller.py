# app/admin/controllers/attendance_controller.py
 
from datetime import date
import calendar
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
 
from app.models.holiday import Holiday
 
 
async def get_attendance_overview_controller(year: int, month: int, db: AsyncSession):
 
   
    last_day = calendar.monthrange(year, month)[1]
 
   
    result = await db.execute(
        select(Holiday).where(
            Holiday.date.between(
                f"{year}-{month:02d}-01",
                f"{year}-{month:02d}-{last_day}"
            )
        )
    )
    holidays = result.scalars().all()
 
   
    holiday_map = {h.date: h.type for h in holidays}
 
    result_data = []
 
    for day in range(1, last_day + 1):
        current_date = date(year, month, day)
 
       
        if current_date in holiday_map:
 
            holiday_type = holiday_map[current_date].strip().lower()
 
       
            if holiday_type in ["public", "public holiday"]:
                day_type = "public_holiday"
 
            elif holiday_type in ["festival", "festival holiday"]:
                day_type = "festival_holiday"
 
            else:
                day_type = "working_day"   # fallback
 
        elif current_date.weekday() >= 5:
            day_type = "weekend"
 
        else:
            day_type = "working_day"
 
        result_data.append({
            "date": current_date.strftime("%Y-%m-%d"),
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