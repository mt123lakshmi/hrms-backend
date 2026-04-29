# app/core/seed_data.py

from sqlalchemy import select
from app.database.database import AsyncSessionLocal

from app.models.day_type import DayType
from app.models.leave_type import LeaveType
from app.models.emp_doctype import DocumentType
from app.models.role import Role


async def seed_master_data():

    print("🔥 SEED FUNCTION CALLED")

    async with AsyncSessionLocal() as db:

        # ==========================
        # DAY TYPES (FIXED)
        # ==========================
        day_types = [
            ("HALF DAY", 0.5),
            ("FULL DAY", 1.0),
        ]

        for name, value in day_types:
            result = await db.execute(
                select(DayType).where(DayType.name == name)
            )
            existing = result.scalar_one_or_none()

            if not existing:
                print(f"Inserting DayType: {name}")
                db.add(DayType(name=name, value=value))
            else:
                # 🔥 UPDATE WRONG VALUES
                if existing.value != value:
                    print(f"Updating DayType: {name}")
                    existing.value = value

        # ==========================
        # LEAVE TYPES (FIXED)
        # ==========================
        leave_types = [
            ("Sick Leave", 1),
            ("Casual Leave", 1),
            ("Earned Leave", 2.5),
        ]

        for name, max_q in leave_types:
            result = await db.execute(
                select(LeaveType).where(LeaveType.name == name)
            )
            existing = result.scalar_one_or_none()

            if not existing:
                print(f"Inserting LeaveType: {name}")
                db.add(LeaveType(name=name, max_per_quarter=max_q))
            else:
                if existing.max_per_quarter != max_q:
                    print(f"Updating LeaveType: {name}")
                    existing.max_per_quarter = max_q

        # ==========================
        # DOCUMENT TYPES (UNCHANGED)
        # ==========================
        doc_types = [
            (1, "SSC"),
            (2, "INTER"),
            (3, "AADHAR"),
            (4, "BTECH MARKLIST"),
            (7, "PASSPORT SIZE PHOTO"),
            (8, "PANCARD"),
        ]

        for doc_id, name in doc_types:
            result = await db.execute(
                select(DocumentType).where(DocumentType.id == doc_id)
            )
            if not result.scalar_one_or_none():
                print(f"Inserting DocumentType: {name}")
                db.add(DocumentType(id=doc_id, name=name))

        # ==========================
        # ROLES (FIXED CASE)
        # ==========================
        roles = ["admin", "Employee"]

        for role in roles:
            result = await db.execute(
                select(Role).where(Role.name == role)
            )
            if not result.scalar_one_or_none():
                print(f"Inserting Role: {role}")
                db.add(Role(name=role))

        print("👉 COMMITTING DATA")
        await db.commit()