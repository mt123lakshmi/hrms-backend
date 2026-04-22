from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from app.models.task import Task
from app.models.work_log import WorkLog
from app.models.taskassignment import TaskAssignment

from app.schemas.employee.worklog_schema import WorkLogResponse


# ==========================
# GET TASKS
# ==========================
async def get_my_tasks(employee_id: int, db: AsyncSession):

    result = await db.execute(
        select(Task, TaskAssignment)
        .join(TaskAssignment, Task.id == TaskAssignment.task_id)
        .where(TaskAssignment.employee_id == employee_id)
    )

    rows = result.all()

    data = []

    for task, assignment in rows:

        # 🔥 get latest worklog for this task
        log_res = await db.execute(
            select(WorkLog)
            .where(
                WorkLog.employee_id == employee_id,
                WorkLog.task_id == task.id
            )
            .order_by(WorkLog.id.desc())
            .limit(1)
        )

        log = log_res.scalar()

        # 🔥 decide status
        if not log:
            status = "ASSIGNED"

        elif log.status == "SUBMITTED":
            status = "PENDING"

        elif log.status == "APPROVED":
            status = "COMPLETED"

        elif log.status == "REJECTED":
            status = "REJECTED"

        else:
            status = "ASSIGNED"

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
# CREATE WORKLOG
# ==========================
async def create_worklog(employee_id: int, data, db: AsyncSession):

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

    # 🔥 IMPORTANT (get ID before commit)
    await db.flush()

    await db.commit()

    # ✅ RETURN FULL FORMATTED RESPONSE
    return WorkLogResponse.from_orm_with_format(log)

# ==========================
# GET HISTORY
# ==========================
async def get_my_history(employee_id: int, db: AsyncSession):

    result = await db.execute(
        select(WorkLog)
        .where(WorkLog.employee_id == employee_id)
        .order_by(WorkLog.date.desc())
    )

    logs = result.scalars().all()

    return [WorkLogResponse.from_orm_with_format(log) for log in logs]