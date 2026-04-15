from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import select
from datetime import datetime

from app.database.database import AsyncSessionLocal
from app.models.leave_balance import LeaveBalance


# 🔹 CURRENT QUARTER
def get_current_quarter_string():
    now = datetime.utcnow()
    quarter = (now.month - 1) // 3 + 1
    return f"{now.year}-Q{quarter}"


# 🔹 ACCRUAL JOB
async def apply_earned_leave_accrual():

    async with AsyncSessionLocal() as db:

        current_quarter = get_current_quarter_string()

        result = await db.execute(select(LeaveBalance))
        balances = result.scalars().all()

        for balance in balances:

            if balance.last_accrual_quarter != current_quarter:
                balance.earned_leave_remaining += 2.5
                balance.last_accrual_quarter = current_quarter

        await db.commit()


# 🔹 START SCHEDULER (QUARTERLY)
def start_scheduler():
    scheduler = AsyncIOScheduler()

    # 🔥 RUN ONLY ON QUARTER START
    scheduler.add_job(
        apply_earned_leave_accrual,
        "cron",
        month="1,4,7,10",   # Jan, Apr, Jul, Oct
        day=1,
        hour=0,
        minute=0
    )

    scheduler.start()

