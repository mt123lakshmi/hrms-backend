from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from datetime import date

from app.models.leave_request import LeaveRequest
from app.models.leave_balance import LeaveBalance
from app.models.holiday import Holiday
from app.models.employee import Employee


async def get_employee_dashboard(db: AsyncSession, current_user):

    try:
        # =========================================================
        # 🔹 GET EMPLOYEE ID
        # =========================================================
        employee_id = current_user.employee_id

        if not employee_id:
            return {
                "success": False,
                "message": "Employee not linked",
                "data": None
            }

        # =========================================================
        # 🔹 FETCH EMPLOYEE
        # =========================================================
        result = await db.execute(
            select(Employee)
            .where(
                Employee.id == employee_id,
                Employee.company_id == current_user.company_id   # 🔥 FIX ADDED
            )
        )
        employee = result.scalar_one_or_none()

        if not employee:
            return {
                "success": False,
                "message": "Employee not found",
                "data": None
            }

        # =========================================================
        # 🔹 LEAVE BALANCE
        # =========================================================
        result = await db.execute(
            select(LeaveBalance).where(
                LeaveBalance.employee_id == employee_id
            )
        )
        balance = result.scalar_one_or_none()

        if not balance:
            balance = LeaveBalance(employee_id=employee_id, total_leaves=18)
            db.add(balance)
            await db.commit()
            await db.refresh(balance)

        total_leaves = balance.total_leaves

        # =========================================================
        # 🔹 APPROVED LEAVES
        # =========================================================
        result = await db.execute(
            select(LeaveRequest).where(
                LeaveRequest.employee_id == employee_id,
                LeaveRequest.status == "Approved"
            )
        )
        approved_leaves = result.scalars().all()

        total_used = float(sum((leave.total_days or 0) for leave in approved_leaves))
        total_remaining = float(total_leaves - total_used)

        total_used = round(total_used, 2)
        total_remaining = round(total_remaining, 2)

        # =========================================================
        # 🔹 PENDING REQUESTS
        # =========================================================
        result = await db.execute(
            select(func.count()).select_from(LeaveRequest).where(
                LeaveRequest.employee_id == employee_id,
                LeaveRequest.status == "Pending"
            )
        )
        pending_requests = result.scalar() or 0

        # =========================================================
        # 🔹 RECENT REQUESTS
        # =========================================================
        result = await db.execute(
            select(LeaveRequest)
            .options(selectinload(LeaveRequest.leave_type))
            .where(LeaveRequest.employee_id == employee_id)
            .order_by(LeaveRequest.start_date.desc())
            .limit(5)
        )
        recent_requests = result.scalars().all()

        recent_data = [
            {
                "start_date": r.start_date,
                "end_date": r.end_date,
                "leave_type": r.leave_type.name if r.leave_type else None,
                "reason": r.reason,
                "status": r.status
            }
            for r in recent_requests
        ]

        # =========================================================
        # 🔹 NEXT HOLIDAY
        # =========================================================
        today = date.today()

        result = await db.execute(
            select(Holiday)
            .where(
                Holiday.date >= today,
                Holiday.company_id == current_user.company_id   # 🔥 FIX ADDED
            )
            .order_by(Holiday.date.asc())
        )
        next_holiday = result.scalars().first()

        holiday_data = None
        if next_holiday:
            holiday_data = {
                "name": next_holiday.name,
                "date": next_holiday.date
            }

        # =========================================================
        # 🔹 FINAL RESPONSE
        # =========================================================
        return {
            "success": True,
            "message": "Dashboard fetched successfully",
            "data": {
                "employee": {
                    "name": employee.name,
                    "emp_id": employee.employee_code,
                    "role": employee.designation
                },
                "leave_balance": total_remaining,
                "leaves_taken": total_used,
                "pending_requests": pending_requests,
                "next_holiday": holiday_data,
                "recent_requests": recent_data
            }
        }

    except Exception as e:
        print("DASHBOARD ERROR:", str(e))

        return {
            "success": False,
            "message": str(e),
            "data": None
        }