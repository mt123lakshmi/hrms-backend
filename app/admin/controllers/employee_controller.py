from datetime import date
import os
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
from app.models.payslip import Payslip
from app.models.role import Role
from app.core.security import hash_password

from app.utils.employee_helper import get_employee_or_404
from app.utils.s3bucket import upload_file_to_s3  # ✅ S3 helper


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
        role_result = await db.execute(
            select(Role).where(Role.id == data["role"])
        )
        role_obj = role_result.scalar_one_or_none()

        if not role_obj:
            raise HTTPException(status_code=400, detail="Invalid role")

        result = await db.execute(
            select(User).where(User.company_email == data["company_email"])
        )
        if result.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Email already exists")

        result = await db.execute(
            select(Employee).where(Employee.employee_code == data["employee_code"])
        )
        if result.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Employee code already exists")

        photo_path = None
        if photo:
            if not photo.content_type.startswith("image/"):
                raise HTTPException(status_code=400, detail="Only image files allowed")

            file_bytes = photo.file.read()

            if not file_bytes:
                raise HTTPException(status_code=400, detail="Empty image")

            content_type = photo.content_type or "image/jpeg"
            unique_name = f"{uuid.uuid4().hex}_{photo.filename}"
            s3_key = f"employee-photos/{unique_name}"

            photo_path = upload_file_to_s3(file_bytes, s3_key, content_type)

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

        db.add(User(
            company_email=data["company_email"],
            password=hash_password(data["password"]),
            role_id=role_obj.id,
            employee_id=emp.id
        ))

        # ✅ FIXED HERE
        db.add(EmployeeFinancialDetail(
            employee_id=emp.id,
            bank_account_number=data["bank_account"],
            bank_name=data.get("bank_name"),
            ifsc_code=data.get("ifsc_code"),
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
        # ===============================
        # 🔹 FETCH EMPLOYEE
        # ===============================
        result = await db.execute(
            select(Employee).where(Employee.id == emp_id)
        )
        employee = result.scalar_one_or_none()

        if not employee:
            raise HTTPException(404, "Employee not found")

        update_data = data if isinstance(data, dict) else data.dict(exclude_unset=True)

        def is_valid(value):
            return value is not None and str(value).strip() != "" and value != "string"

        # ===============================
        # 🔹 FETCH USER
        # ===============================
        result = await db.execute(
            select(User).where(User.employee_id == emp_id)
        )
        user_obj = result.scalar_one_or_none()

        # ===============================
        # 🔹 BASIC FIELD UPDATE
        # ===============================
        for field in ["name", "phone_number", "address", "company_email", "personal_email"]:
            if field in update_data and is_valid(update_data[field]):
                setattr(employee, field, update_data[field])

        if "designation" in update_data and is_valid(update_data["designation"]):
            employee.designation = update_data["designation"]

        # ===============================
        # 🔹 USER UPDATE
        # ===============================
        if user_obj:
            if "company_email" in update_data and is_valid(update_data["company_email"]):
                user_obj.company_email = update_data["company_email"]

            if "password" in update_data and is_valid(update_data["password"]):
                user_obj.password = hash_password(update_data["password"])

        # ===============================
        # 🔹 PHOTO UPDATE (S3)
        # ===============================
        if photo:
            if not photo.content_type.startswith("image/"):
                raise HTTPException(status_code=400, detail="Only image files allowed")

            file_bytes = photo.file.read()
            if not file_bytes:
                raise HTTPException(status_code=400, detail="Empty image")

            content_type = photo.content_type or "image/jpeg"
            s3_key = f"employee-photos/{uuid.uuid4().hex}_{photo.filename}"

            employee.photo = upload_file_to_s3(file_bytes, s3_key, content_type)

        # ===============================
        # 🔹 FINANCIAL UPDATE
        # ===============================
        result = await db.execute(
            select(EmployeeFinancialDetail).where(
                EmployeeFinancialDetail.employee_id == emp_id
            )
        )
        financial = result.scalar_one_or_none()

        if financial:
            if "bank_account" in update_data and is_valid(update_data.get("bank_account")):
                financial.bank_account_number = update_data.get("bank_account")

            if "bank_name" in update_data and is_valid(update_data.get("bank_name")):
                financial.bank_name = update_data.get("bank_name")

            if "ifsc_code" in update_data and is_valid(update_data.get("ifsc_code")):
                financial.ifsc_code = update_data.get("ifsc_code")

            if "pan_number" in update_data and is_valid(update_data.get("pan_number")):
                financial.pan_number = update_data.get("pan_number")

            if "uan_number" in update_data and is_valid(update_data.get("uan_number")):
                financial.uan_pf_number = update_data.get("uan_number")

        # ===============================
        # 🔹 ASSET UPDATE (FIXED)
        # ===============================
        result = await db.execute(
            select(EmployeeAsset).where(EmployeeAsset.employee_id == emp_id)
        )
        asset = result.scalar_one_or_none()

        if asset:
            if "access_card" in update_data and is_valid(update_data.get("access_card")):
                asset.access_card = update_data.get("access_card")

            if "laptop_id" in update_data and is_valid(update_data.get("laptop_id")):
                asset.laptop_asset_id = update_data.get("laptop_id")

            if "assets" in update_data and is_valid(update_data.get("assets")):
                asset.additional_asset = update_data.get("assets")

            # update status dynamically
            has_asset = any([
                is_valid(asset.access_card),
                is_valid(asset.laptop_asset_id),
                is_valid(asset.additional_asset)
            ])

            asset.status = "assigned" if has_asset else "unassigned"

        else:
            # create asset if not exists
            has_asset = any([
                is_valid(update_data.get("access_card")),
                is_valid(update_data.get("laptop_id")),
                is_valid(update_data.get("assets"))
            ])

            db.add(EmployeeAsset(
                employee_id=emp_id,
                access_card=update_data.get("access_card"),
                laptop_asset_id=update_data.get("laptop_id"),
                additional_asset=update_data.get("assets"),
                status="assigned" if has_asset else "unassigned"
            ))

        # ===============================
        # 🔹 COMMIT
        # ===============================
        await db.commit()

        return {
            "success": True,
            "message": "Employee updated successfully"
        }

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
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