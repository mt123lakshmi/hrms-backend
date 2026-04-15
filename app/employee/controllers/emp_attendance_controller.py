from datetime import date, timedelta
import calendar
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
 
from app.models.holiday import Holiday
from app.models.leave_request import LeaveRequest
 
 
async def get_attendance_calendar(year: int, month: int, db: AsyncSession, user):
 
    # =========================================================
    # 🔹 BASIC DATE RANGE
    # =========================================================
    num_days = calendar.monthrange(year, month)[1]
 
    start_date = date(year, month, 1)
    end_date = date(year, month, num_days)
 
    # =========================================================
    # 🔹 FETCH HOLIDAYS
    # =========================================================
    result = await db.execute(
        select(Holiday).where(
            Holiday.date >= start_date,
            Holiday.date <= end_date
        )
    )
    holidays = result.scalars().all()
 
    # normalize type
    holiday_map = {h.date: (h.type or "").lower() for h in holidays}
 
    # =========================================================
    # 🔹 FETCH APPROVED LEAVES
    # =========================================================
    result = await db.execute(
        select(LeaveRequest).where(
            LeaveRequest.employee_id == user.employee_id,
            LeaveRequest.status == "Approved",
            LeaveRequest.start_date <= end_date,
            LeaveRequest.end_date >= start_date
        )
    )
    leaves = result.scalars().all()
 
    # =========================================================
    # 🔹 BUILD LEAVE DATE SET (EXCLUDING WEEKENDS)
    # =========================================================
    leave_dates = set()
 
    for leave in leaves:
        current = leave.start_date
 
        while current <= leave.end_date:
            # EXCLUDE WEEKENDS
            if current.weekday() < 5:
                leave_dates.add(current)
 
            current += timedelta(days=1)
 
    # =========================================================
    # 🔹 BUILD FINAL CALENDAR RESPONSE
    # =========================================================
    data = []
 
    for day in range(1, num_days + 1):
        current_date = date(year, month, day)
 
        # 🔥 STRICT PRIORITY
        if current_date in leave_dates:
            day_type = "leave"
 
        elif current_date in holiday_map:
            if holiday_map[current_date] == "public":
                day_type = "public_holiday"
            else:
                day_type = "festival_holiday"
 
        elif current_date.weekday() >= 5:
            day_type = "weekend"
 
        else:
            day_type = "working_day"
 
        # ✅ RETURN EXTRA FLAGS (IMPORTANT FOR FRONTEND)
        data.append({
            "date": str(current_date),
            "type": day_type,
            "is_leave": day_type == "leave",
            "is_weekend": current_date.weekday() >= 5,
            "is_holiday": current_date in holiday_map
        })
 
    # =========================================================
    # 🔹 FINAL RESPONSE
    # =========================================================
    return {
        "success": True,
        "data": data
    }
 