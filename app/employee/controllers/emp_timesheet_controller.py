from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException
from datetime import date as dt_date, datetime, timedelta

from app.models.timesheet import TimeSheet
from app.models.employee import Employee   # 🔥 ADDED
from app.utils.time_utils import calculate_duration


def format_time(t):
    if not t:
        return None
    return t.strftime("%I:%M %p")


# =========================
# 🔹 VALIDATE EMPLOYEE (COMMON)
# =========================
async def validate_employee(db, employee_id, current_user):

    result = await db.execute(
        select(Employee).where(
            Employee.id == employee_id,
            Employee.company_id == current_user.company_id
        )
    )

    employee = result.scalar_one_or_none()

    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")


# =========================
# UPSERT TIMESHEET
# =========================
async def upsert_timesheet(db: AsyncSession, employee_id: int, data, current_user):

    # 🔥 VALIDATE EMPLOYEE
    await validate_employee(db, employee_id, current_user)

    if not (data.check_in or data.check_out or data.work_update):
        raise HTTPException(
            status_code=400,
            detail="Provide at least one field (check_in, check_out, work_update)"
        )

    if data.date > dt_date.today():
        raise HTTPException(status_code=400, detail="Future date not allowed")

    stmt = select(TimeSheet).where(
        TimeSheet.employee_id == employee_id,
        TimeSheet.date == data.date
    )

    result = await db.execute(stmt)
    ts = result.scalar_one_or_none()

    # =========================
    # CREATE
    # =========================
    if not ts:

        ts = TimeSheet(
            employee_id=employee_id,
            date=data.date,
            check_in=data.check_in,
            check_out=data.check_out,
            work_update=data.work_update,
            work_status="Pending",
            approval_status="Pending"
        )

        if ts.check_in and ts.check_out:
            check_in_dt = datetime.combine(ts.date, ts.check_in)
            check_out_dt = datetime.combine(ts.date, ts.check_out)

            if check_out_dt <= check_in_dt:
                raise HTTPException(status_code=400, detail="Invalid check-out time")

            ts.duration = calculate_duration(ts.check_in, ts.check_out)

        db.add(ts)

    # =========================
    # UPDATE
    # =========================
    else:

        if data.check_in and ts.check_in:
            raise HTTPException(status_code=400, detail="Already checked in")

        if data.check_in and not ts.check_in:
            ts.check_in = data.check_in

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

        if data.work_update:
            ts.work_update = data.work_update

        if ts.check_in and ts.check_out:
            ts.duration = calculate_duration(ts.check_in, ts.check_out)

    await db.commit()
    await db.refresh(ts)

    return {"message": "Timesheet updated successfully"}


# =========================
# GET TIMESHEETS
# =========================
async def get_employee_timesheets(db: AsyncSession, employee_id: int, current_user):

    # 🔥 VALIDATE EMPLOYEE
    await validate_employee(db, employee_id, current_user)

    last_45_days = datetime.now().date() - timedelta(days=45)

    stmt = (
        select(TimeSheet)
        .where(
            TimeSheet.employee_id == employee_id,
            TimeSheet.date >= last_45_days
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