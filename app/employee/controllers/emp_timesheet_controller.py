from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException
from datetime import date as dt_date, datetime,timedelta

from app.models.timesheet import TimeSheet
from app.utils.time_utils import calculate_duration


def format_time(t):
    if not t:
        return None
    return t.strftime("%I:%M %p")


# =========================
# UPSERT TIMESHEET
# =========================
async def upsert_timesheet(db: AsyncSession, employee_id: int, data):

    # ✅ FIXED: allow work_update also
    if not (data.check_in or data.check_out or data.work_update):
        raise HTTPException(
            status_code=400,
            detail="Provide at least one field (check_in, check_out, work_update)"
        )

    # ✅ PREVENT FUTURE DATE
    if data.date > dt_date.today():
        raise HTTPException(status_code=400, detail="Future date not allowed")

    stmt = select(TimeSheet).where(
        TimeSheet.employee_id == employee_id,
        TimeSheet.date == data.date
    )

    result = await db.execute(stmt)
    ts = result.scalar_one_or_none()

    # =========================
    # CREATE (NEW ENTRY)
    # =========================
    if not ts:

        # ❌ REMOVED: forcing check-in first

        ts = TimeSheet(
            employee_id=employee_id,
            date=data.date,
            check_in=data.check_in,
            check_out=data.check_out,
            work_update=data.work_update,
            work_status="Pending",
            approval_status="Pending"
        )

        # ✅ VALIDATE + CALCULATE DURATION
        if ts.check_in and ts.check_out:
            check_in_dt = datetime.combine(ts.date, ts.check_in)
            check_out_dt = datetime.combine(ts.date, ts.check_out)

            if check_out_dt <= check_in_dt:
                raise HTTPException(status_code=400, detail="Invalid check-out time")

            ts.duration = calculate_duration(ts.check_in, ts.check_out)

        db.add(ts)

    # =========================
    # UPDATE (EXISTING ENTRY)
    # =========================
    else:

        # ❌ prevent duplicate check-in
        if data.check_in and ts.check_in:
            raise HTTPException(status_code=400, detail="Already checked in")

        # ✅ ALLOW CHECK-IN IF MISSING
        if data.check_in and not ts.check_in:
            ts.check_in = data.check_in

        # ✅ CHECK-OUT LOGIC
        if data.check_out:
            if not ts.check_in:
                raise HTTPException(status_code=400, detail="Check-in missing")

            if ts.check_out:
                raise HTTPException(status_code=400, detail="Already checked out")

            check_in_dt = datetime.combine(ts.date, ts.check_in)
            check_out_dt = datetime.combine(ts.date, data.check_out)

            if check_out_dt <= check_in_dt:
                raise HTTPException(status_code=400, detail="Invalid check-out time")

            ts.check_out = data.check_out

        # ✅ FIXED: allow work_update independently
        if data.work_update:
            ts.work_update = data.work_update

        # ✅ CALCULATE DURATION
        if ts.check_in and ts.check_out:
            ts.duration = calculate_duration(ts.check_in, ts.check_out)

    await db.commit()
    await db.refresh(ts)

    return {"message": "Timesheet updated successfully"}


# =========================
# GET TIMESHEETS
# =========================
async def get_employee_timesheets(db: AsyncSession, employee_id: int):

    last_45_days = datetime.now().date() - timedelta(days=45)

    stmt = (
        select(TimeSheet)
        .where(
            TimeSheet.employee_id == employee_id,
            TimeSheet.date >= last_45_days   # ✅ THIS IS THE FIX
        )
        .order_by(TimeSheet.date.desc())
    )

    result = await db.execute(stmt)
    records = result.scalars().all()

    return [
        {
            "id": r.id,
            "date": r.date,
            "check_in": format_time(r.check_in),
            "check_out": format_time(r.check_out),
            "duration": r.duration,
            "work_update": r.work_update,
            "approval_status": r.approval_status,
            "rejection_reason": r.rejection_reason
        }
        for r in records
    ]