from sqlalchemy import select
from app.database.database import AsyncSessionLocal
from app.models.user import User
from app.models.role import Role   # ✅ IMPORTANT
from app.core.security import hash_password


async def create_admin():
    async with AsyncSessionLocal() as db:

        # 🔹 Check if admin user already exists
        result = await db.execute(
            select(User).where(User.company_email == "admin@gmail.com")
        )
        existing_admin = result.scalar_one_or_none()

        if existing_admin:
            return

        # 🔹 Get admin role from DB
        result = await db.execute(
            select(Role).where(Role.name == "admin")
        )
        admin_role = result.scalar_one_or_none()

     
        if not admin_role:
            admin_role = Role(name="admin")
            db.add(admin_role)
            await db.flush()   # ✅ get ID without commit

        # 🔹 Create admin user with role_id
        admin = User(
            company_email="admin@gmail.com",
            password=hash_password("admin1234"),
            role_id=admin_role.id   
        )

        db.add(admin)
        await db.commit()
        await db.refresh(admin)