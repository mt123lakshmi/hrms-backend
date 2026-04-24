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


async def send_payslip_email(email: str, file_url: str):

    message = MessageSchema(
        subject="Payslip Uploaded",
        recipients=[email],
        body=f"""
Dear Employee,

Your payslip has been generated and uploaded.

👉 Download your payslip here:
{file_url}

Regards,  
HR Team
        """,
        subtype=MessageType.plain
    )

    fm = FastMail(conf)
    await fm.send_message(message)


async def send_timesheet_rejection_email(email: str, log):

    message = MessageSchema(
        subject="Timesheet Rejected",
        recipients=[email],
        body=f"""
Your timesheet has been rejected.

Date: {log.date}
Check-in: {log.check_in}
Check-out: {log.check_out}

Reason:
{log.rejection_reason}

Please update and resubmit.
        """,
        subtype="plain"
    )

    fm = FastMail(conf)
    await fm.send_message(message)