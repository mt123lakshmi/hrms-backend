from datetime import date
import os
import shutil
import uuid
from sqlalchemy.orm import selectinload
from fastapi import HTTPException
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.employee_document import EmployeeDocument
from app.models.employee import Employee
from app.models.leave_request import LeaveRequest
from app.models.user import User
from app.models.employee_asset import EmployeeAsset
from app.models.employee_financial import EmployeeFinancialDetail
from app.models.employee_document import EmployeeDocument
from app.models.payslip import Payslip
from app.models.role import Role
from app.core.security import hash_password

from app.utils.employee_helper import get_employee_or_404

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


# ===============================
# 🔹 EMPLOYEE LIST
# ===============================
async def get_employee_list_controller(db: AsyncSession, user):

    if not user.role or user.role.name != "admin":
        raise HTTPException(403, "Admin only")

    today = date.today()

    result = await db.execute(select(Employee))
    employees = result.scalars().all()

    leave_result = await db.execute(
        select(LeaveRequest.employee_id)
        .where(
            LeaveRequest.status == "approved",
            LeaveRequest.start_date <= today,
            LeaveRequest.end_date >= today
        )
    )
    leave_ids = {row[0] for row in leave_result.all()}

    final_result = []

    for emp in employees:
        status = "Inactive" if emp.id in leave_ids else "Active"

        final_result.append({
            "id": emp.id,
            "name": emp.name,
            "email": emp.company_email,
            "employee_code": emp.employee_code,
            "designation": emp.designation,  
            "status": status,
            "photo": emp.photo
        })

    return {"success": True, "data": final_result}


# ===============================
# 🔹 CREATE EMPLOYEE
# ===============================
async def create_employee_controller(data, photo, db, user):

    if not user.role or user.role.name != "admin":
        raise HTTPException(status_code=403, detail="Admin only")

    try:
        # ROLE VALIDATION
        role_result = await db.execute(
            select(Role).where(Role.id == data["role"])
        )
        role_obj = role_result.scalar_one_or_none()

        if not role_obj:
            raise HTTPException(status_code=400, detail="Invalid role")

        # EMAIL CHECK
        result = await db.execute(
            select(User).where(User.company_email == data["company_email"])
        )
        if result.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Email already exists")

        # EMPLOYEE CODE CHECK
        result = await db.execute(
            select(Employee).where(Employee.employee_code == data["employee_code"])
        )
        if result.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Employee code already exists")

        photo_path = None
        if photo:
            if not photo.content_type.startswith("image/"):
                raise HTTPException(status_code=400, detail="Only image files allowed")

            filename = f"{uuid.uuid4()}_{photo.filename}"
            file_location = os.path.join("uploads", filename)

            with open(file_location, "wb") as buffer:
                shutil.copyfileobj(photo.file, buffer)

            photo_path = file_location

        # CREATE EMPLOYEE
        emp = Employee(
            employee_code=data["employee_code"],
            name=data["name"],
            phone_number=data["phone_number"],
            address=data["address"],
            company_email=data["company_email"],
            personal_email=data["personal_email"],
            designation=data["designation"],  
            photo=photo_path
        )

        db.add(emp)
        await db.flush()

        # CREATE USER
        db.add(User(
            company_email=data["company_email"],
            password=hash_password(data["password"]),
            role_id=role_obj.id,
            employee_id=emp.id
        ))

        # FINANCIAL
        db.add(EmployeeFinancialDetail(
            employee_id=emp.id,
            bank_account_number=data["bank_account"],
            bank_name="Default Bank",
            ifsc_code="IFSC0001",
            pan_number=data["pan_number"],
            uan_pf_number=data["uan_number"]
        ))
        def is_valid(val):
            return val not in [None, "", "string"]

        has_asset = any([
            is_valid(data.get("access_card")),
            is_valid(data.get("laptop_id")),
            is_valid(data.get("assets"))
        ])


        # ASSETS
        db.add(EmployeeAsset(
            employee_id=emp.id,
            access_card=data.get("access_card"),
            laptop_asset_id=data.get("laptop_id"),
            additional_asset=data["assets"],
            status="assigned" if has_asset else "unassigned"
        ))

        await db.commit()

        return {
            "success": True,
            "message": "Employee created successfully",
            "employee_id": emp.id
        }

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# ===============================
# 🔹 EMPLOYEE PROFILE
# ===============================
async def get_employee_full_profile(employee_id: int, db, user):

    if user.role and user.role.name == "employee":
        if user.employee_id != employee_id:
            raise HTTPException(403, "Access denied")

    result = await db.execute(
        select(Employee)
        .options(
            selectinload(Employee.financial_detail),
            selectinload(Employee.assets),
            selectinload(Employee.documents).selectinload(EmployeeDocument.document_type),
            selectinload(Employee.payslips),
        )
        .where(Employee.id == employee_id)
    )

    employee = result.scalar_one_or_none()

    if not employee:
        raise HTTPException(404, "Employee not found")

    return {
        "basic": {
            "id": employee.id,
            "name": employee.name,
            "company_email": employee.company_email,
            "personal_email": employee.personal_email,
            "phone": employee.phone_number,
            "employee_code": employee.employee_code,
            "designation": employee.designation,
            "photo": employee.photo
        },

        "financial": {
            "bank_account": employee.financial_detail.bank_account_number if employee.financial_detail else None,
            "bank_name": employee.financial_detail.bank_name if employee.financial_detail else None,
            "ifsc": employee.financial_detail.ifsc_code if employee.financial_detail else None,
            "pan": employee.financial_detail.pan_number if employee.financial_detail else None,
            "uan": employee.financial_detail.uan_pf_number if employee.financial_detail else None,
        },

        "assets": [
            {
                "access_card": a.access_card,
                "laptop_id": a.laptop_asset_id,
                "status": a.status
            }
            for a in (employee.assets or [])
        ],

        "documents": [
            {
                "type": d.document_type.name if d.document_type else None,
                "file": d.file_path
            }
            for d in (employee.documents or [])
        ],

        "payslips": [
            {
                "id": p.id,
                "month": p.month,
                "file": p.file_path
            }
            for p in (employee.payslips or [])
        ]
    }
# ===============================
# 🔹 UPDATE EMPLOYEE
# ===============================
# ===============================
# 🔹 UPDATE EMPLOYEE
# ===============================
async def update_employee_controller(emp_id, data, photo, db: AsyncSession, user):

    if not user.role or user.role.name != "admin":
        raise HTTPException(403, "Admin only")

    try:
        # 🔹 GET EMPLOYEE
        result = await db.execute(
            select(Employee).where(Employee.id == emp_id)
        )
        employee = result.scalar_one_or_none()

        if not employee:
            raise HTTPException(404, "Employee not found")

        update_data = data if isinstance(data, dict) else data.dict(exclude_unset=True)

        # ✅ FIXED VALIDATION
        def is_valid(value):
            return value not in [None, "", "string"]

        # 🔹 FETCH USER ONCE
        result = await db.execute(
            select(User).where(User.employee_id == emp_id)
        )
        user_obj = result.scalar_one_or_none()

        # ===============================
        # 🔹 BASIC FIELDS
        # ===============================
        for field in [
            "name", "phone_number", "address",
            "company_email", "personal_email"
        ]:
            if field in update_data and is_valid(update_data[field]):
                setattr(employee, field, update_data[field])

        # ===============================
        # 🔥 SYNC EMAIL WITH USER TABLE
        # ===============================
        if "company_email" in update_data and is_valid(update_data["company_email"]):
            if user_obj:
                user_obj.company_email = update_data["company_email"]

        # ===============================
        # 🔹 DESIGNATION (STRING)
        # ===============================
        if "designation" in update_data and is_valid(update_data["designation"]):
            employee.designation = update_data["designation"]

        # ===============================
        # 🔹 PASSWORD
        # ===============================
        if "password" in update_data and is_valid(update_data["password"]):
            if user_obj:
                user_obj.password = hash_password(update_data["password"])

        # ===============================
        # 🔹 PHOTO
        # ===============================
        if photo:
            if not photo.content_type.startswith("image/"):
                raise HTTPException(400, "Only image files allowed")

            filename = f"{uuid.uuid4()}_{photo.filename}"
            file_location = os.path.join(UPLOAD_DIR, filename)

            with open(file_location, "wb") as buffer:
                shutil.copyfileobj(photo.file, buffer)

            employee.photo = file_location

        # ===============================
        # 🔹 UPDATE ASSETS (FIXED)
        # ===============================
        result = await db.execute(
            select(EmployeeAsset).where(EmployeeAsset.employee_id == emp_id)
        )
        asset_obj = result.scalar_one_or_none()

        def is_valid_asset(val):
            return val not in [None, "", "string"]

        has_asset = any([
            is_valid_asset(update_data.get("access_card")),
            is_valid_asset(update_data.get("laptop_id")),
            is_valid_asset(update_data.get("assets"))
        ])

        if asset_obj:
            if "access_card" in update_data:
                asset_obj.access_card = update_data.get("access_card")

            if "laptop_id" in update_data:
                asset_obj.laptop_asset_id = update_data.get("laptop_id")

            if "assets" in update_data:
                asset_obj.additional_asset = update_data.get("assets")

            # ✅ FIXED STATUS LOGIC
            asset_obj.status = "assigned" if any([
                is_valid_asset(asset_obj.access_card),
                is_valid_asset(asset_obj.laptop_asset_id),
                is_valid_asset(asset_obj.additional_asset)
            ]) else "unassigned"

        else:
            if has_asset:
                db.add(EmployeeAsset(
                    employee_id=emp_id,
                    access_card=update_data.get("access_card"),
                    laptop_asset_id=update_data.get("laptop_id"),
                    additional_asset=update_data.get("assets"),
                    status="assigned"
                ))

        # 🔹 SAVE
        await db.commit()

        return {
            "success": True,
            "message": "Employee updated successfully"
        }

    except Exception as e:
        await db.rollback()
        return {
            "success": False,
            "message": str(e)
        }
# ===============================
# 🔹 DELETE EMPLOYEE
# ===============================
async def delete_employee_controller(emp_id, db: AsyncSession, user):

    if not user.role or user.role.name != "admin":
        raise HTTPException(403, "Admin only")

    employee, error = await get_employee_or_404(emp_id, db)
    if error:
        return error

    await db.execute(delete(EmployeeAsset).where(EmployeeAsset.employee_id == emp_id))
    await db.execute(delete(EmployeeFinancialDetail).where(EmployeeFinancialDetail.employee_id == emp_id))
    await db.execute(delete(EmployeeDocument).where(EmployeeDocument.employee_id == emp_id))
    await db.execute(delete(LeaveRequest).where(LeaveRequest.employee_id == emp_id))
    await db.execute(delete(Payslip).where(Payslip.employee_id == emp_id))
    await db.execute(delete(User).where(User.employee_id == emp_id))

    await db.delete(employee)
    await db.commit()

    return {"success": True}