# app/admin/controllers/dashboard_controller.py
 
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy import select, func

from sqlalchemy.orm import selectinload

from datetime import date

from fastapi import HTTPException
 
from app.models.employee import Employee

from app.models.leave_request import LeaveRequest

from app.models.holiday import Holiday
 
from app.core.response import success_response, error_response
 
 
async def get_dashboard_controller(db: AsyncSession, user):

    try:

        today = date.today()
 
        # 🔹 Total Employees

        result = await db.execute(

            select(func.count(Employee.id))

        )

        total_employees = result.scalar()
 
        # 🔹 Pending Leaves

        result = await db.execute(

            select(func.count(LeaveRequest.id))

            .where(LeaveRequest.status == "pending")

        )

        leaves_pending = result.scalar()
 
        # 🔹 On Leave Today

        result = await db.execute(

            select(func.count(LeaveRequest.id)).where(

                LeaveRequest.start_date <= today,

                LeaveRequest.end_date >= today,

                LeaveRequest.status == "approved"

            )

        )

        on_leave_today = result.scalar()
 
        # 🔹 Upcoming Holidays

        result = await db.execute(

            select(func.count(Holiday.id))

            .where(Holiday.date >= today)

        )

        upcoming_holidays = result.scalar()
 
        # 🔹 Pending Leave List (✅ FIXED HERE)

        result = await db.execute(

            select(LeaveRequest)

            .options(

                selectinload(LeaveRequest.employee),

                selectinload(LeaveRequest.leave_type)  # ✅ important fix

            )

            .where(LeaveRequest.status == "pending")

        )

        pending_leaves = result.scalars().all()
 
        # 🔹 Build Response (✅ FIXED HERE)

        leave_list = [

            {

                "employee_name": leave.employee.name if leave.employee else None,

                "leave_type": leave.leave_type.name if leave.leave_type else None,  # ✅ fix

                "start_date": leave.start_date,

                "end_date": leave.end_date,

                "reason": leave.reason,

                "status": leave.status

            }

            for leave in pending_leaves

        ]
 
        data = {

            "total_employees": total_employees,

            "leaves_pending": leaves_pending,

            "on_leave_today": on_leave_today,

            "upcoming_holidays": upcoming_holidays,

            "pending_leaverequest": leave_list

        }
 
        return success_response(data, "Dashboard fetched successfully")
 
    except HTTPException as e:

        raise e
 
    except Exception as e:

        return error_response(f"Dashboard error: {str(e)}", 500)
 