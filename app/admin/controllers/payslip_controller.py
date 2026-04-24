import uuid
from datetime import datetime

from fastapi import HTTPException, UploadFile, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.payslip import Payslip
from app.models.employee import Employee

# S3
from app.utils.s3bucket import (
    upload_file_to_s3,
    extract_s3_key,
    generate_presigned_download_url
)

# Email
from app.utils.send_email import send_payslip_email


# ===============================
# 🔹 COMMON S3 UPLOAD
# ===============================
async def handle_payslip_upload(file: UploadFile, employee_id: int, month: str):

    if not file:
        raise HTTPException(status_code=400, detail="File is required")

    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF allowed")

    file_bytes = await file.read()

    if not file_bytes:
        raise HTTPException(status_code=400, detail="Empty file uploaded")

    content_type = file.content_type or "application/pdf"

    unique_name = f"{employee_id}_{month}_{uuid.uuid4().hex}.pdf"
    s3_key = f"payslips/{unique_name}"

    return upload_file_to_s3(file_bytes, s3_key, content_type)


# ===============================
# 🔹 GET EMPLOYEES
# ===============================
async def get_employees_with_payslips(db: AsyncSession):

    result = await db.execute(select(Employee))
    employees = result.scalars().all()

    return {
        "success": True,
        "data": [
            {
                "employee_id": e.id,
                "employee_code": e.employee_code,
                "name": e.name,
                "designation": e.designation
            }
            for e in employees
        ]
    }


# ===============================
# 🔹 GET EMPLOYEE PAYSLIPS
# ===============================
async def get_employee_payslips(employee_id: int, db: AsyncSession, user):

    if user.role == "employee" and user.employee_id != employee_id:
        raise HTTPException(status_code=403, detail="Not allowed")

    result = await db.execute(
        select(Payslip, Employee)
        .join(Employee, Payslip.employee_id == Employee.id)
        .where(Payslip.employee_id == employee_id)
    )

    records = result.all()

    return {
        "success": True,
        "data": [
            {
                "payslip_id": p.id,
                "employee_id": e.id,
                "employee_code": e.employee_code,
                "employee_name": e.name,
                "designation": e.designation,
                "month": p.month,
                "uploaded_date": p.uploaded_at.date() if p.uploaded_at else None,
                "file_url": p.file_path
            }
            for p, e in records
        ]
    }


# ===============================
# 🔹 UPLOAD PAYSLIP (FIXED EMAIL)
# ===============================
async def upload_payslip(
    employee_id: int,
    month: str,
    file: UploadFile,
    db: AsyncSession,
    background_tasks: BackgroundTasks   # ✅ added
):

    # 🔹 validate month
    try:
        if len(month) == 7:
            parsed_date = datetime.strptime(month, "%Y-%m")
        elif len(month) == 10:
            parsed_date = datetime.strptime(month, "%Y-%m-%d")
        else:
            raise ValueError()

        formatted_month = parsed_date.strftime("%B_%Y").lower()

    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Month must be YYYY-MM or YYYY-MM-DD"
        )

    # 🔹 duplicate check
    result = await db.execute(
        select(Payslip).where(
            Payslip.employee_id == employee_id,
            Payslip.month == formatted_month
        )
    )
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Payslip already exists")

    # 🔹 employee check
    result = await db.execute(
        select(Employee).where(Employee.id == employee_id)
    )
    employee = result.scalar_one_or_none()

    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    # 🔹 upload to S3
    file_url = await handle_payslip_upload(file, employee_id, formatted_month)

    payslip = Payslip(
        employee_id=employee_id,
        month=formatted_month,
        file_path=file_url,
        uploaded_at=datetime.utcnow()
    )

    db.add(payslip)
    await db.commit()
    await db.refresh(payslip)

    # 🔥 FIXED EMAIL (reliable)
    if employee.company_email:
        background_tasks.add_task(
            send_payslip_email,
            employee.company_email,
            file_url
        )

    return {
        "success": True,
        "message": "Payslip uploaded",
        "data": {
            "payslip_id": payslip.id,
            "file_url": file_url
        }
    }


# ===============================
# 🔹 UPDATE PAYSLIP
# ===============================
async def update_payslip(
    payslip_id: int,
    file: UploadFile,
    db: AsyncSession
):

    result = await db.execute(
        select(Payslip).where(Payslip.id == payslip_id)
    )
    payslip = result.scalar_one_or_none()

    if not payslip:
        raise HTTPException(status_code=404, detail="Payslip not found")

    file_url = await handle_payslip_upload(
        file,
        payslip.employee_id,
        payslip.month
    )

    payslip.file_path = file_url
    payslip.uploaded_at = datetime.utcnow()

    await db.commit()
    await db.refresh(payslip)

    return {
        "success": True,
        "message": "Payslip updated",
        "data": {
            "payslip_id": payslip.id,
            "file_url": file_url
        }
    }


# ===============================
# 🔹 DOWNLOAD PAYSLIP
# ===============================
async def download_payslip(payslip_id: int, db: AsyncSession, user):

    result = await db.execute(
        select(Payslip).where(Payslip.id == payslip_id)
    )
    payslip = result.scalar_one_or_none()

    if not payslip:
        raise HTTPException(status_code=404, detail="Payslip not found")

    if user.role == "employee" and user.employee_id != payslip.employee_id:
        raise HTTPException(status_code=403, detail="Not allowed")

    file_key = extract_s3_key(payslip.file_path)
    download_url = generate_presigned_download_url(file_key)

    return {
        "success": True,
        "download_url": download_url
    }