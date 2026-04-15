import random
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.user import User
from app.utils.send_email import send_otp_email

from app.core.security import hash_password
# 🔥 STEP 1 — SEND OTP
async def send_otp(db: AsyncSession, email: str):

    result = await db.execute(select(User).where(User.company_email  == email))
    user = result.scalar_one_or_none()

    if not user:
        return {"error": "User not found"}

    otp = str(random.randint(100000, 999999))

    user.otp = otp
    user.otp_expiry = datetime.utcnow() + timedelta(minutes=5)

    await db.commit()

    # 🔥 Send email
    await send_otp_email(email, otp)

    return {"message": "OTP sent to your email"}


# 🔥 STEP 2 — RESET PASSWORD
async def reset_password(db, email, otp, new_password, confirm_password):

    result = await db.execute(
        select(User).where(User.company_email == email)
    )
    user = result.scalar_one_or_none()

    if not user:
        return {"error": "User not found"}

    if user.otp != otp:
        return {"error": "Invalid OTP"}

    if datetime.utcnow() > user.otp_expiry:
        return {"error": "OTP expired"}

    if new_password != confirm_password:
        return {"error": "Passwords do not match"}

    # 🔥 IMPORTANT: match your login logic
    user.password = hash_password(new_password)

    user.otp = None
    user.otp_expiry = None

    await db.commit()
    await db.refresh(user)

    return {"message": "Password updated"}