from fastapi import HTTPException
from sqlalchemy import select, extract
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.leave_request import LeaveRequest
from app.models.leave_balance import LeaveBalance
from app.models.leave_type import LeaveType
from app.models.employee import Employee

from calendar import month_abbr
from datetime import datetime


# ===============================
# 🔹 GET ALL LEAVES (ADMIN)
# ===============================
async def get_leave_list_controller(db: AsyncSession):

    result = await db.execute(
        select(
            LeaveRequest.id,
            LeaveRequest.employee_id,
            Employee.name.label("employee_name"),
            LeaveType.name.label("leave_type"),
            LeaveRequest.start_date,
            LeaveRequest.end_date,
            LeaveRequest.reason,
            LeaveRequest.status,
            LeaveRequest.rejection_reason
        )
        .join(Employee, LeaveRequest.employee_id == Employee.id)
        .outerjoin(LeaveType, LeaveRequest.leave_type_id == LeaveType.id)
    )

    leaves = result.all()

    return {
        "success": True,
        "data": [
            {
                "leave_id": l.id,
                "employee_id": l.employee_id,
                "employee_name": l.employee_name,
                "leave_type": l.leave_type if l.leave_type else "unknown",
                "date_range": f"{l.start_date} — {l.end_date}",
                "reason": l.reason,
                "status": l.status,
                "rejection_reason": l.rejection_reason
            }
            for l in leaves
        ]
    }


# ===============================
# 🔹 GET INSIGHTS (ADMIN)
# ===============================
async def get_leave_insights(employee_id: int, db: AsyncSession):

    TOTAL_LEAVES = 18  # safe for now

    result = await db.execute(
        select(LeaveRequest)
        .options(selectinload(LeaveRequest.leave_type))
        .where(LeaveRequest.employee_id == employee_id)
    )

    all_leaves = result.scalars().all()

    approved_leaves = [
        l for l in all_leaves
        if l.status and l.status.strip().lower() == "approved"
    ]

    now = datetime.utcnow()
    current_year = now.year
    current_month = now.month

    quarter = (current_month - 1) // 3 + 1

    quarter_map = {
        1: [1, 2, 3],
        2: [4, 5, 6],
        3: [7, 8, 9],
        4: [10, 11, 12]
    }

    months_in_quarter = quarter_map[quarter]

    total_used = 0
    quarter_used = 0
    monthly = {m: 0 for m in months_in_quarter}

    leave_types = {
        "casual": 0,
        "sick": 0,
        "earned": 0
    }

    for l in approved_leaves:

        # ✅ correct day calculation
        days = (
            l.total_days
            if l.total_days
            else (l.end_date - l.start_date).days + 1
        )

        total_used += days

        if not l.leave_type:
            continue

        name = l.leave_type.name.lower()

        if "earned" in name:
            leave_types["earned"] += days
        elif "casual" in name:
            leave_types["casual"] += days
        elif "sick" in name:
            leave_types["sick"] += days

        if l.start_date.year == current_year:
            if l.start_date.month in months_in_quarter:
                quarter_used += days
                monthly[l.start_date.month] += days

    ordered = list(months_in_quarter)

    response_months = {
        month_abbr[ordered[2]].lower(): monthly[ordered[2]],
        month_abbr[ordered[1]].lower(): monthly[ordered[1]],
        month_abbr[ordered[0]].lower(): monthly[ordered[0]],
    }

    remaining_leaves = TOTAL_LEAVES - total_used
    if remaining_leaves < 0:
        remaining_leaves = 0

    leave_history = [
        {
            "date_range": f"{l.start_date} — {l.end_date}",
            "type": l.leave_type.name if l.leave_type else "unknown",
            "reason": l.reason,
            "status": l.status
        }
        for l in all_leaves
    ]

    return {
        "success": True,
        "data": {
            "total_leaves": TOTAL_LEAVES,
            "used_leaves": total_used,
            "remaining_leaves": remaining_leaves,
            "this_quarter": quarter_used,
            "monthly": response_months,
            "leave_types": leave_types,
            "leave_history": leave_history
        }
    }


# ===============================
# 🔹 APPROVE / REJECT (ADMIN)
# ===============================
async def leave_action_controller(
    leave_id: int,
    action: str,
    db: AsyncSession,
    reason: str = None,
    admin_id: int = None
):

    result = await db.execute(
        select(LeaveRequest)
        .options(selectinload(LeaveRequest.leave_type))
        .where(LeaveRequest.id == leave_id)
    )
    leave = result.scalar_one_or_none()

    if not leave:
        raise HTTPException(status_code=404, detail="Leave not found")

    if leave.status.lower() != "pending":
        raise HTTPException(
            status_code=400,
            detail=f"Leave already {leave.status}"
        )

    if action.lower() not in ["approved", "rejected"]:
        raise HTTPException(status_code=400, detail="Invalid action")

    if not leave.leave_type:
        raise HTTPException(
            status_code=400,
            detail="Leave type mapping missing"
        )

    leave_type = leave.leave_type

    # ✅ FIXED DAY CALCULATION
    requested_days = (
        leave.total_days
        if leave.total_days
        else (leave.end_date - leave.start_date).days + 1
    )

    # ===============================
    # 🔴 SICK & CASUAL VALIDATION (FIXED)
    # ===============================
    if leave_type.max_per_quarter:

        result = await db.execute(
            select(LeaveRequest).where(
                LeaveRequest.employee_id == leave.employee_id,
                LeaveRequest.leave_type_id == leave.leave_type_id,

                # ✅ FIX 1: ONLY APPROVED
                LeaveRequest.status == "Approved",

                # ✅ FIX 2: EXCLUDE CURRENT LEAVE
                LeaveRequest.id != leave.id,

                extract('quarter', LeaveRequest.start_date) == extract('quarter', leave.start_date),
                extract('year', LeaveRequest.start_date) == extract('year', leave.start_date)
            )
        )

        existing = result.scalars().all()

        if len(existing) >= leave_type.max_per_quarter:
            raise HTTPException(
                status_code=400,
                detail=f"{leave_type.name} already used this quarter"
            )

    # ===============================
    # 🔴 EARNED LEAVE
    # ===============================
    if leave_type.name.strip().lower() == "earned":

        balance = await db.scalar(
            select(LeaveBalance).where(
                LeaveBalance.employee_id == leave.employee_id
            )
        )

        if not balance:
            raise HTTPException(
                status_code=400,
                detail="Leave balance not found"
            )

        current_quarter = get_current_quarter_string()

        if balance.last_accrual_quarter != current_quarter:
            balance.earned_leave_remaining += 2.5
            balance.last_accrual_quarter = current_quarter

        if balance.earned_leave_remaining < requested_days:
            raise HTTPException(
                status_code=400,
                detail="Insufficient earned leave balance"
            )

        balance.earned_leave_used += requested_days
        balance.earned_leave_remaining -= requested_days

    # ===============================
    # 🔹 FINAL UPDATE
    # ===============================
    leave.status = action.capitalize()

    if action.lower() == "rejected":
        if not reason:
            raise HTTPException(
                status_code=400,
                detail="Rejection reason required"
            )
        leave.rejection_reason = reason
    else:
        leave.rejection_reason = None

    if admin_id:
        leave.approved_by = admin_id

    await db.commit()
    await db.refresh(leave)

    return {
        "success": True,
        "message": f"Leave {leave.status} successfully",
        "data": {
            "leave_id": leave.id,
            "status": leave.status,
            "rejection_reason": leave.rejection_reason
        }
    }