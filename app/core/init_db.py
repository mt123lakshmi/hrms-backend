# app/core/init_db.py

from sqlalchemy import select
from app.database.database import AsyncSessionLocal

from app.models.user import User
from app.models.role import Role
from app.models.company import Company

from app.core.security import hash_password


async def create_admin():
    async with AsyncSessionLocal() as db:

        # =========================
        # 1. CREATE COMPANIES
        # =========================

        result = await db.execute(
            select(Company).where(Company.name == "Ameya")
        )
        company_a = result.scalar_one_or_none()

        if not company_a:
            company_a = Company(name="Ameya")
            db.add(company_a)
            await db.flush()


        result = await db.execute(
            select(Company).where(Company.name == "Jaitra Media")
        )
        company_b = result.scalar_one_or_none()

        if not company_b:
            company_b = Company(name="Jaitra Media")
            db.add(company_b)
            await db.flush()


        # =========================
        # 2. CREATE ADMIN ROLE
        # =========================

        result = await db.execute(
            select(Role).where(Role.name == "admin")
        )
        admin_role = result.scalar_one_or_none()

        if not admin_role:
            admin_role = Role(name="admin")
            db.add(admin_role)
            await db.flush()


        # =========================
        # 3. CREATE ADMIN A (Ameya)
        # =========================

        result = await db.execute(
            select(User).where(User.company_email == "saivinayganesula@gmail.com")
        )
        admin_a = result.scalar_one_or_none()

        if not admin_a:
            admin_a = User(
                company_email="saivinayganesula@gmail.com",
                password=hash_password("vinay"),
                role_id=admin_role.id,
                company_id=company_a.id   # 🔥 Ameya
            )
            db.add(admin_a)


        # =========================
        # 4. CREATE ADMIN B (Jaitra Media)
        # =========================

        result = await db.execute(
            select(User).where(User.company_email == "thotameghanalakshmi@gmail.com")
        )
        admin_b = result.scalar_one_or_none()

        if not admin_b:
            admin_b = User(
                company_email="thotameghanalakshmi@gmail.com",
                password=hash_password("meghana"),
                role_id=admin_role.id,
                company_id=company_b.id   # 🔥 Jaitra Media
            )
            db.add(admin_b)


        # =========================
        # 5. COMMIT
        # =========================

        await db.commit()