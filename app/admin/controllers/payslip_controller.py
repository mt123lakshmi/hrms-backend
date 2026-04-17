import os
import uuid
from fastapi import HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
import asyncio   # ✅ added

from app.models.payslip import Payslip
from app.models.employee import Employee

# ✅ IMPORT EMAIL FUNCTION
from app.utils.send_email import send_payslip_email


# ===============================
# 🔹 PATH SETUP
# ===============================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads", "payslips")


# ===============================
# 🔹 GET EMPLOYEE LIST
# ===============================
async def get_employees_with_payslips(db: AsyncSession):

    result = await db.execute(
        select(Employee)
    )

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
# 🔹 UPLOAD PAYSLIP (UPDATED WITH EMAIL)
# ===============================
async def upload_payslip(
    employee_id: int,
    month: str,
    file: UploadFile,
    db: AsyncSession
):

    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF allowed")

    # 🔹 validate month
    try:
        if len(month) == 7:
            parsed_date = datetime.strptime(month, "%Y-%m")
        elif len(month) == 10:
            parsed_date = datetime.strptime(month, "%Y-%m-%d")
        else:
            raise ValueError()

        formatted_month = parsed_date.strftime("%B %Y")

    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Month must be YYYY-MM or YYYY-MM-DD"
        )

    # 🔹 check duplicate
    result = await db.execute(
        select(Payslip).where(
            Payslip.employee_id == employee_id,
            Payslip.month == formatted_month
        )
    )
    existing = result.scalar_one_or_none()

    if existing:
        raise HTTPException(status_code=400, detail="Payslip already exists")

    # 🔹 fetch employee
    result = await db.execute(
        select(Employee).where(Employee.id == employee_id)
    )
    employee = result.scalar_one_or_none()

    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    os.makedirs(UPLOAD_DIR, exist_ok=True)

    safe_month = formatted_month.replace(" ", "_").lower()
    unique_id = str(uuid.uuid4())[:8]
    filename = f"{employee_id}_{safe_month}_{unique_id}.pdf"

    file_path = os.path.join(UPLOAD_DIR, filename)

    with open(file_path, "wb") as f:
        f.write(await file.read())

    relative_path = f"uploads/payslips/{filename}"
    now = datetime.utcnow()

    payslip = Payslip(
        employee_id=employee_id,
        month=formatted_month,
        file_path=relative_path,
        uploaded_at=now
    )

    db.add(payslip)
    await db.commit()
    await db.refresh(payslip)

    # ===============================
    # 🔥 SEND EMAIL (ADDED)
    # ===============================
    if employee.company_email:
        try:
            asyncio.create_task(
                send_payslip_email(employee.company_email, file_path)
            )
        except Exception as e:
            print("Email failed:", str(e))   # don't break API

    return {
        "success": True,
        "message": "Payslip uploaded",
        "data": {
            "payslip_id": payslip.id,
            "file_url": relative_path
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

    if not file or not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Valid PDF required")

    old_path = os.path.join(BASE_DIR, payslip.file_path)
    if os.path.exists(old_path):
        os.remove(old_path)

    safe_month = payslip.month.replace(" ", "_").lower()
    unique_id = str(uuid.uuid4())[:8]
    filename = f"{payslip.employee_id}_{safe_month}_{unique_id}.pdf"

    new_path = os.path.join(UPLOAD_DIR, filename)

    with open(new_path, "wb") as f:
        f.write(await file.read())

    relative_path = f"uploads/payslips/{filename}"
    payslip.file_path = relative_path
    payslip.uploaded_at = datetime.utcnow()

    await db.commit()
    await db.refresh(payslip)

    return {
        "success": True,
        "message": "Payslip updated",
        "data": {
            "payslip_id": payslip.id,
            "file_url": relative_path
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

    absolute_path = os.path.join(BASE_DIR, payslip.file_path)

    if not os.path.exists(absolute_path):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        path=absolute_path,
        filename=os.path.basename(absolute_path),
        media_type="application/pdf",
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0"
        }
    )