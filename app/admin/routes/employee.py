from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional   # ✅ ADD THIS

from app.database.database import get_db
from app.core.dependencies import admin_required

from app.admin.controllers.employee_controller import (
    get_employee_list_controller,
    create_employee_controller,
    get_employee_full_profile,
    update_employee_controller,
    delete_employee_controller
)

router = APIRouter(prefix="/admin/employee", tags=["Admin Employee"])


# ===============================
# 🔹 GET EMPLOYEES
# ===============================
@router.get("/")
async def get_employee_list(
    db: AsyncSession = Depends(get_db),
    user=Depends(admin_required)
):
    return await get_employee_list_controller(db, user)


# ===============================
# 🔹 CREATE EMPLOYEE (FIXED)
# ===============================
@router.post("/")
async def create_employee(
    employee_code: str = Form(...),
    name: str = Form(...),
    phone_number: str = Form(...),
    address: str = Form(...),
    company_email: str = Form(...),
    personal_email: str = Form(...),
    designation: str = Form(...),

    password: str = Form(...),
    role: int = Form(...),
    bank_account: str = Form(...),
    pan_number: str = Form(...),
    uan_number: str = Form(...),

    # ✅ ONLY THESE 3 CHANGED (made optional)
    access_card: Optional[str] = Form(None),
    laptop_id: Optional[str] = Form(None),
    assets: Optional[str] = Form(None),

    photo: UploadFile = File(None),

    db: AsyncSession = Depends(get_db),
    user=Depends(admin_required)
):

    data = {
        "employee_code": employee_code,
        "name": name,
        "phone_number": phone_number,
        "address": address,
        "company_email": company_email,
        "personal_email": personal_email,
        "designation": designation,

        "password": password,
        "role": role,
        "bank_account": bank_account,
        "pan_number": pan_number,
        "uan_number": uan_number,

        # stays same (no break)
        "access_card": access_card,
        "laptop_id": laptop_id,
        "assets": assets,
    }

    return await create_employee_controller(data, photo, db, user)


# ===============================
# 🔹 GET PROFILE
# ===============================
@router.get("/{emp_id}")
async def employee_profile(
    emp_id: int,
    db: AsyncSession = Depends(get_db),
    user=Depends(admin_required)
):
    return await get_employee_full_profile(emp_id, db, user)


# ===============================
# 🔹 UPDATE EMPLOYEE (already correct)
# ===============================
@router.patch("/{emp_id}")
async def update_employee(
    emp_id: int,
    name: str = Form(None),
    phone_number: str = Form(None),
    address: str = Form(None),
    company_email: str = Form(None),
    personal_email: str = Form(None),
    designation: str = Form(None),

    password: str = Form(None),
    bank_account: str = Form(None),
    pan_number: str = Form(None),
    uan_number: str = Form(None),

    # already optional ✔️
    access_card: str = Form(None),
    laptop_id: str = Form(None),
    assets: str = Form(None),

    photo: UploadFile = File(None),

    db: AsyncSession = Depends(get_db),
    user=Depends(admin_required)
):

    data = {
        "name": name,
        "phone_number": phone_number,
        "address": address,
        "company_email": company_email,
        "personal_email": personal_email,
        "designation": designation,

        "password": password,
        "bank_account": bank_account,
        "pan_number": pan_number,
        "uan_number": uan_number,

        "access_card": access_card,
        "laptop_id": laptop_id,
        "assets": assets,
    }

    return await update_employee_controller(emp_id, data, photo, db, user)


# ===============================
# 🔹 DELETE EMPLOYEE
# ===============================
@router.delete("/{emp_id}")
async def delete_employee(
    emp_id: int,
    db: AsyncSession = Depends(get_db),
    user=Depends(admin_required)
):
    return await delete_employee_controller(emp_id, db, user)