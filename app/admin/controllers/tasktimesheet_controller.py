from sqlalchemy import select, func
from app.models.employee import Employee
from app.models.task import Task
from app.models.work_log import WorkLog
from app.models.taskassignment import TaskAssignment

from datetime import datetime
# =========================================================
# GET ALL EMPLOYEES (OPTIMIZED)
# =========================================================
async def get_all_employees(db):

    res = await db.execute(select(Employee))
    employees = res.scalars().all()

    data = []

    for emp in employees:

        latest = await db.execute(
            select(WorkLog.status)
            .where(WorkLog.employee_id == emp.id)
            .order_by(WorkLog.id.desc())
            .limit(1)
        )

        status = latest.scalar()

        # 🔥 clean mapping
        if not status:
            status = "NO SUBMISSION"
        elif status == "SUBMITTED":
            status = "PENDING"
        elif status == "APPROVED":
            status = "COMPLETED"
        elif status == "REJECTED":
            status = "REJECTED"
        else:
            status = "UNKNOWN"

        data.append({
            "id": emp.id,
            "name": emp.name,
            "designation": emp.designation,
            "emp_code": emp.employee_code,
            "status": status
        })

    return data


# =========================================================
# EMPLOYEE DASHBOARD
# =========================================================
async def get_task_dashboard(emp_id, db):

    emp = await db.get(Employee, emp_id)

    if not emp:
        return {"error": "Employee not found"}

    # ======================
    # EXISTING (UNCHANGED)
    # ======================
    tasks = await db.scalar(
        select(func.count()).where(TaskAssignment.employee_id == emp_id)
    )

    approved = await db.scalar(
        select(func.count()).where(
            WorkLog.employee_id == emp_id,
            WorkLog.status == "APPROVED"
        )
    )

    pending = await db.scalar(
        select(func.count()).where(
            WorkLog.employee_id == emp_id,
            WorkLog.status == "SUBMITTED"
        )
    )

    rejected = await db.scalar(
        select(func.count()).where(
            WorkLog.employee_id == emp_id,
            WorkLog.status == "REJECTED"
        )
    )

    total = (approved or 0) + (rejected or 0)

    # =========================================================
    # 🔥 ADD THIS BLOCK ONLY (DO NOT TOUCH ABOVE CODE)
    # =========================================================
    logs_result = await db.execute(
        select(WorkLog)
        .where(WorkLog.employee_id == emp_id)
        .order_by(WorkLog.date.desc())
    )

    logs = logs_result.scalars().all()

    timesheets = []

    for log in logs:

        duration = None
        if log.check_in and log.check_out:
            delta = datetime.combine(log.date, log.check_out) - datetime.combine(log.date, log.check_in)
            hours = delta.seconds // 3600
            minutes = (delta.seconds % 3600) // 60
            duration = f"{hours}h {minutes}m"

        status_map = {
            "SUBMITTED": "Pending",
            "APPROVED": "Approved",
            "REJECTED": "Rejected"
        }

        timesheets.append({
            "id": log.id,
            "date": log.date.strftime("%Y-%m-%d"),
            "check_in": log.check_in.strftime("%H:%M") if log.check_in else None,
            "check_out": log.check_out.strftime("%H:%M") if log.check_out else None,
            "duration": duration,
            "description": log.description,
            "proof": log.proof,
            "status": status_map.get(log.status),
            "reason": log.rejection_reason
        })

    # =========================================================
    # FINAL RESPONSE (JUST ADD ONE FIELD)
    # =========================================================
    return {
        "employee": {
            "id": emp.id,
            "name": emp.name,
            "email": emp.company_email,
            "designation": emp.designation
        },
        "summary": {
            "tasks_assigned": tasks or 0,
            "completed": approved or 0,
            "pending": pending or 0
        },
        "analytics": {
            "approved_percent": round((approved / total) * 100, 2) if total else 0,
            "rejected_percent": round((rejected / total) * 100, 2) if total else 0
        },

        # 🔥 ONLY ADD THIS LINE
        "timesheets": timesheets
    }

# =========================================================
# ASSIGN TASK (SAFE)
# =========================================================
async def assign_task(data, db):

    # 🔥 validation
    if data.start_date > data.end_date:
        return {"error": "Start date cannot be after end date"}

    emp = await db.get(Employee, data.employee_id)
    if not emp:
        return {"error": "Employee not found"}

    task = Task(
        title=data.title,
        description=data.description,
        start_date=data.start_date,
        end_date=data.end_date,
        frequency=data.frequency
    )

    db.add(task)
    await db.flush()

    assign = TaskAssignment(
        task_id=task.id,
        employee_id=data.employee_id,
        status="ASSIGNED",
        assigned_at=datetime.now() 
    )

    db.add(assign)
    await db.commit()

    return {
        "message": "Task assigned successfully",
        "task_id": task.id
    }


# =========================================================
# APPROVE WORKLOG
# =========================================================
async def approve_worklog(worklog_id, db):

    log = await db.get(WorkLog, worklog_id)

    if not log:
        return {"error": "Worklog not found"}

    log.status = "APPROVED"
    log.rejection_reason = None

    await db.commit()

    return {"message": "Worklog approved"}


# =========================================================
# REJECT WORKLOG
# =========================================================
async def reject_worklog(worklog_id, reason, db):

    log = await db.get(WorkLog, worklog_id)

    if not log:
        return {"error": "Worklog not found"}

    log.status = "REJECTED"
    log.rejection_reason = reason

    await db.commit()

    return {"message": "Worklog rejected"}