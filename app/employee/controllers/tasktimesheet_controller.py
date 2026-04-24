from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, date

from app.models.task import Task
from app.models.work_log import WorkLog
from app.models.taskassignment import TaskAssignment

from app.schemas.employee.worklog_schema import WorkLogResponse


# ==========================
# GET TASKS (FIXED)
# ==========================
async def get_my_tasks(employee_id: int, db: AsyncSession):

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
async def create_worklog(employee_id: int, data, db: AsyncSession):

    task = await db.get(Task, data.task_id)

    if not task:
        return {"error": "Task not found"}

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
# GET HISTORY (UNCHANGED)
# ==========================
async def get_my_history(employee_id: int, db: AsyncSession):

    result = await db.execute(
        select(WorkLog)
        .where(WorkLog.employee_id == employee_id)
        .order_by(WorkLog.date.desc())
    )

    logs = result.scalars().all()

    return [WorkLogResponse.from_orm_with_format(log) for log in logs]