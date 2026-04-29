from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, extract, and_
from datetime import timedelta
from fastapi import HTTPException

from app.models.leave_request import LeaveRequest
from app.models.leave_type import LeaveType
from app.models.leave_balance import LeaveBalance
from app.models.day_type import DayType
from app.models.employee import Employee   # 🔥 ADDED


# =========================================================
# 🔹 WORKING DAYS CALCULATION
# =========================================================
def calculate_working_days(start_date, end_date):
    total_days = 0
    current = start_date

    while current <= end_date:
        if current.weekday() < 5:
            total_days += 1
        current += timedelta(days=1)

    return total_days


# =========================================================
# 🔹 GET ALL LEAVES
# =========================================================
async def get_employee_leaves(db: AsyncSession, current_user):

    employee_id = current_user.employee_id

    # 🔥 VALIDATE EMPLOYEE (CRITICAL)
    result = await db.execute(
        select(Employee).where(
            Employee.id == employee_id,
            Employee.company_id == current_user.company_id
        )
    )
    employee = result.scalar_one_or_none()

    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    result = await db.execute(
        select(LeaveRequest, LeaveType.name)
        .join(LeaveType, LeaveRequest.leave_type_id == LeaveType.id)
        .where(LeaveRequest.employee_id == employee_id)
        .order_by(LeaveRequest.start_date.desc())
    )

    rows = result.all()

    data = []
    for leave, type_name in rows:
        data.append({
            "id": leave.id,
            "start_date": leave.start_date,
            "end_date": leave.end_date,
            "type": type_name,
            "day_type_id": leave.day_type_id,
            "reason": leave.reason,
            "status": leave.status,
            "total_days": leave.total_days,
            "approved_by": leave.approved_by,
            "rejection_reason": leave.rejection_reason
        })

    return {
        "success": True,
        "message": "Leave data fetched",
        "data": data
    }


# =========================================================
# 🔹 VALIDATION
# =========================================================
async def validate_leave_request(db, current_user, employee_id, leave_type_id, start_date, end_date):

    # 🔥 VALIDATE EMPLOYEE AGAIN (SAFE PRACTICE)
    emp_check = await db.execute(
        select(Employee).where(
            Employee.id == employee_id,
            Employee.company_id == current_user.company_id
        )
    )
    employee = emp_check.scalar_one_or_none()

    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    # 🔹 Leave Type
    leave_type = await db.get(LeaveType, leave_type_id)

    if not leave_type:
        raise HTTPException(status_code=400, detail="Invalid leave type")

    # 🔹 Max per quarter
    if leave_type.max_per_quarter:
        result = await db.execute(
            select(LeaveRequest).where(
                LeaveRequest.employee_id == employee_id,
                LeaveRequest.leave_type_id == leave_type_id,
                LeaveRequest.status.in_(["pending", "approved"]),
                extract('quarter', LeaveRequest.start_date) == extract('quarter', start_date),
                extract('year', LeaveRequest.start_date) == extract('year', start_date)
            )
        )

        existing = result.scalars().all()

        if len(existing) >= leave_type.max_per_quarter:
            raise HTTPException(
                status_code=400,
                detail=f"{leave_type.name} leave already used this quarter"
            )

    # 🔹 Earned leave balance (FIXED)
    if leave_type.name.lower() == "earned":

        requested_days = (end_date - start_date).days + 1

        balance = await db.scalar(
            select(LeaveBalance).where(
                LeaveBalance.employee_id == employee_id
            )
        )

        if not balance or balance.total_leaves < requested_days:
            raise HTTPException(
                status_code=400,
                detail="Insufficient earned leave balance"
            )

    # 🔹 Overlap check
    overlap_result = await db.execute(
        select(LeaveRequest).where(
            LeaveRequest.employee_id == employee_id,
            LeaveRequest.status.in_(["pending", "approved"]),
            and_(
                LeaveRequest.start_date <= end_date,
                LeaveRequest.end_date >= start_date
            )
        )
    )

    overlapping = overlap_result.scalars().all()

    if overlapping:
        raise HTTPException(
            status_code=400,
            detail="Leave dates overlap with existing leave"
        )


# =========================================================
# 🔹 CREATE LEAVE
# =========================================================
async def create_leave_request(db: AsyncSession, current_user, payload):

    employee_id = current_user.employee_id

    # 🔥 VALIDATE EMPLOYEE
    result = await db.execute(
        select(Employee).where(
            Employee.id == employee_id,
            Employee.company_id == current_user.company_id
        )
    )
    employee = result.scalar_one_or_none()

    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    if payload.start_date > payload.end_date:
        return {
            "success": False,
            "message": "Start date cannot be after end date",
            "data": None
        }

    # 🔹 Day type
    day_type = await db.get(DayType, payload.day_type_id)
    if not day_type:
        raise HTTPException(status_code=400, detail="Invalid day type")

    # 🔥 Half day validation
    if day_type.name.lower() == "half" and payload.start_date != payload.end_date:
        raise HTTPException(
            status_code=400,
            detail="Half day leave must be for a single day"
        )

    # 🔹 Total days
    if day_type.name.lower() == "half":
        total_days = 0.5
    else:
        total_days = calculate_working_days(
            payload.start_date,
            payload.end_date
        )

    if total_days == 0:
        return {
            "success": False,
            "message": "Selected dates are only weekends",
            "data": None
        }

    # 🔹 Business validation
    await validate_leave_request(
        db,
        current_user,
        employee_id,
        payload.leave_type_id,
        payload.start_date,
        payload.end_date
    )

    # 🔹 Create leave
    new_leave = LeaveRequest(
        employee_id=employee_id,
        leave_type_id=payload.leave_type_id,
        day_type_id=payload.day_type_id,
        start_date=payload.start_date,
        end_date=payload.end_date,
        reason=payload.reason,
        status="pending",
        total_days=total_days
    )

    db.add(new_leave)
    await db.commit()
    await db.refresh(new_leave)

    return {
        "success": True,
        "message": "Leave request submitted",
        "data": {
            "id": new_leave.id,
            "status": new_leave.status,
            "total_days": total_days
        }
    }