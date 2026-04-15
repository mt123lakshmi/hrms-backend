from fastapi_mail import FastMail, MessageSchema
from app.core.config import conf


async def send_otp_email(email: str, otp: str):

    message = MessageSchema(
        subject="Password Reset OTP",
        recipients=[email],
        body=f"""
Your OTP is: {otp}

This OTP will expire in 5 minutes.
Do not share it with anyone.
        """,
        subtype="plain"
    )

    fm = FastMail(conf)
    await fm.send_message(message)