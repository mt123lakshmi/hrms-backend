from fastapi_mail import FastMail, MessageSchema, MessageType
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


async def send_payslip_email(email: str, file_path: str):

    message = MessageSchema(
        subject="Payslip Uploaded",
        recipients=[email],
        body="""
Dear Employee,

Your payslip has been generated and uploaded.

Please find the attached payslip.

Regards,  
HR Team
        """,
        subtype=MessageType.plain,

        attachments=[file_path]   # 🔥 THIS IS IMPORTANT
    )

    fm = FastMail(conf)
    await fm.send_message(message)