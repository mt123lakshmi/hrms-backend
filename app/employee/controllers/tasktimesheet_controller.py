from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, date
from fastapi import HTTPException

from app.models.task import Task
from app.models.work_log import WorkLog
from app.models.taskassignment import TaskAssignment
from app.models.employee import Employee   

from app.schemas.employee.worklog_schema import WorkLogResponse


# =========================================================
# 🔹 VALIDATE EMPLOYEE (COMMON)
# =========================================================
async def validate_employee(db, employee_id, current_user):

    result = await db.execute(
        select(Employee).where(
            Employee.id == employee_id,
            Employee.company_id == current_user.company_id   # 🔥 CRITICAL
        )
    )

    employee = result.scalar_one_or_none()

    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")


# ==========================
# GET TASKS (FIXED)
# ==========================
async def get_my_tasks(employee_id: int, db: AsyncSession, current_user):

    # 🔥 VALIDATE EMPLOYEE
    await validate_employee(db, employee_id, current_user)

    result = await db.execute(
        select(Task, TaskAssignment)
        .join(TaskAssignment, Task.id == TaskAssignment.task_id)
        .where(TaskAssignment.employee_id == employee_id)
    )

    rows = result.all()
    today = date.today()

    data = []

    for task, assignment in rows:

        if today <= task.end_date:
            status = "PENDING"

        else:
            logs_res = await db.execute(
                select(WorkLog.status).where(
                    WorkLog.employee_id == employee_id,
                    WorkLog.task_id == task.id
                )
            )
            logs = logs_res.scalars().all()

            if logs and all(l == "APPROVED" for l in logs):
                status = "COMPLETED"

            elif any(l == "REJECTED" for l in logs):
                status = "REJECTED"

            else:
                status = "PENDING"

        data.append({
            "task_id": task.id,
            "title": task.title,
            "description": task.description,
            "start_date": task.start_date,
            "end_date": task.end_date,
            "status": status,
            "assigned_at": assignment.assigned_at.strftime("%I:%M %p") if assignment.assigned_at else None
        })

    return data


# ==========================
# CREATE WORKLOG (FIXED)
# ==========================
async def create_worklog(employee_id: int, data, db: AsyncSession, current_user):

    # 🔥 VALIDATE EMPLOYEE
    await validate_employee(db, employee_id, current_user)

    task = await db.get(Task, data.task_id)

    if not task:
        return {"error": "Task not found"}

    # 🔥 OPTIONAL SAFETY (if tasks are company-based)
    if hasattr(task, "company_id") and task.company_id != current_user.company_id:
        raise HTTPException(status_code=403, detail="Access denied")

    # 🔥 CHECK TASK ASSIGNED TO EMPLOYEE
    assignment = await db.execute(
        select(TaskAssignment).where(
            TaskAssignment.employee_id == employee_id,
            TaskAssignment.task_id == data.task_id
        )
    )

    if not assignment.scalar():
        raise HTTPException(status_code=403, detail="Task not assigned to employee")

    if data.date < task.start_date or data.date > task.end_date:
        return {"error": "Cannot log outside task date range"}

    existing = await db.execute(
        select(WorkLog).where(
            WorkLog.employee_id == employee_id,
            WorkLog.task_id == data.task_id,
            WorkLog.date == data.date
        )
    )

    if existing.scalar():
        return {"error": "Already logged for this task today"}

    if data.check_in and data.check_out:
        if data.check_out <= data.check_in:
            return {"error": "Check-out must be after check-in"}

    log = WorkLog(
        employee_id=employee_id,
        task_id=data.task_id,
        date=data.date,
        check_in=data.check_in,
        check_out=data.check_out,
        description=data.description,
        proof=data.proof,
        status="SUBMITTED"
    )

    db.add(log)
    await db.flush()
    await db.commit()

    return WorkLogResponse.from_orm_with_format(log)


# ==========================
# GET HISTORY (UNCHANGED + SAFE)
# ==========================
async def get_my_history(employee_id: int, db: AsyncSession, current_user):

    # 🔥 VALIDATE EMPLOYEE
    await validate_employee(db, employee_id, current_user)

    result = await db.execute(
        select(WorkLog)
        .where(WorkLog.employee_id == employee_id)
        .order_by(WorkLog.date.desc())
    )

    logs = result.scalars().all()  

    return [WorkLogResponse.from_orm_with_format(log) for log in logs]