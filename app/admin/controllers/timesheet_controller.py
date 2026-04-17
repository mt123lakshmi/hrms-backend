from sqlalchemy.orm import Session
from sqlalchemy import select, func, and_
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.timesheet import TimeSheet
from app.models.employee import Employee
from app.utils.time_utils import calculate_duration


# ✅ GET LATEST TIMESHEET PER EMPLOYEE (LIST VIEW)
async def get_latest_timesheets(db: AsyncSession):

    subquery = (
        select(
            TimeSheet.employee_id,
            func.max(TimeSheet.date).label("latest_date")
        )
        .group_by(TimeSheet.employee_id)
        .subquery()
    )

    stmt = (
        select(Employee, TimeSheet)
        .outerjoin(subquery, Employee.id == subquery.c.employee_id)
        .outerjoin(
            TimeSheet,
            and_(
                TimeSheet.employee_id == subquery.c.employee_id,
                TimeSheet.date == subquery.c.latest_date
            )
        )
    )

    result = await db.execute(stmt)
    records = result.all()

    data = []

    for emp, ts in records:

        data.append({
            "employee": {
                "name": emp.name,
                "code": emp.employee_code,
                "designation": emp.designation
            },

            "latest_entry": {
                "timesheet_id": ts.id if ts else None,   # ✅ ADDED

                "date": ts.date if ts else None,
                "day": ts.date.strftime("%a") if ts else None,

                "check_in": ts.check_in.strftime("%I:%M %p") if ts and ts.check_in else None,
                "check_out": ts.check_out.strftime("%I:%M %p") if ts and ts.check_out else None,

                "duration": calculate_duration(ts.check_in, ts.check_out) if ts else None,
                "work_update": ts.work_update if ts else None,

                "work_status": ts.work_status if ts else "No Entry",
                "approval_status": ts.approval_status if ts else "No Entry"
            }
        })

    return data


# ✅ GET SINGLE EMPLOYEE LATEST
async def get_latest_timesheet_by_employee(
    db: AsyncSession,
    employee_id: int
):

    latest_date = await db.scalar(
        select(func.max(TimeSheet.date)).where(
            TimeSheet.employee_id == employee_id
        )
    )

    if not latest_date:
        raise HTTPException(404, "No timesheet found")

    stmt = (
        select(TimeSheet, Employee)
        .join(Employee, Employee.id == TimeSheet.employee_id)
        .where(
            TimeSheet.employee_id == employee_id,
            TimeSheet.date == latest_date
        )
    )

    result = await db.execute(stmt)
    record = result.first()

    if not record:
        raise HTTPException(404, "Timesheet not found")

    ts, emp = record

    return {
        "employee": {
            "name": emp.name,
            "code": emp.employee_code,
            "designation": emp.designation
        },
        "latest_entry": {
            "timesheet_id": ts.id,   # ✅ ADDED

            "date": ts.date,
            "day": ts.date.strftime("%a"),

            "check_in": ts.check_in.strftime("%I:%M %p") if ts.check_in else None,
            "check_out": ts.check_out.strftime("%I:%M %p") if ts.check_out else None,

            "duration": calculate_duration(ts.check_in, ts.check_out),
            "work_update": ts.work_update,
            "work_status": ts.work_status,
            "approval_status": ts.approval_status
        }
    }


# ✅ GET HISTORY
async def get_employee_history(db: AsyncSession, employee_id: int):

    stmt = (
        select(TimeSheet, Employee)
        .join(Employee, Employee.id == TimeSheet.employee_id)
        .where(TimeSheet.employee_id == employee_id)
        .order_by(TimeSheet.date.desc())
    )

    result = await db.execute(stmt)
    records = result.all()

    if not records:
        return []   # ✅ FIXED (no exception)

    data = []

    for ts, emp in records:
        data.append({
            "timesheet_id": ts.id,   # ✅ ADDED

            "employee_name": emp.name,
            "employee_code": emp.employee_code,
            "designation": emp.designation,

            "date": ts.date,
            "check_in": ts.check_in,
            "check_out": ts.check_out,
            "duration": calculate_duration(ts.check_in, ts.check_out),

            "work_update": ts.work_update,
            "work_status": ts.work_status,
            "approval_status": ts.approval_status,
            "rejection_reason": ts.rejection_reason
        })

    return data


# ✅ APPROVE / REJECT
async def timesheet_action(
    db: AsyncSession,
    timesheet_id: int,
    action: str,
    reason: str = None
):

    result = await db.execute(
        select(TimeSheet).where(TimeSheet.id == timesheet_id)
    )
    ts = result.scalar_one_or_none()

    if not ts:
        raise HTTPException(status_code=404, detail="Timesheet not found")

    if not ts.check_in or not ts.check_out:
        raise HTTPException(
            status_code=400,
            detail="Employee must check-in and check-out first"
        )

    if action.lower() == "approve":
        ts.approval_status = "Approved"
        ts.rejection_reason = None
        ts.work_status = "Completed"

    elif action.lower() == "reject":
        if not reason:
            raise HTTPException(
                status_code=400,
                detail="Rejection reason is required"
            )

        ts.approval_status = "Rejected"
        ts.rejection_reason = reason
        ts.work_status = "Pending"

    else:
        raise HTTPException(
            status_code=400,
            detail="Invalid action"
        )

    await db.commit()
    await db.refresh(ts)

    return {
        "message": f"Timesheet {action}d successfully",
        "timesheet_id": ts.id,
        "approval_status": ts.approval_status,
        "work_status": ts.work_status
    }