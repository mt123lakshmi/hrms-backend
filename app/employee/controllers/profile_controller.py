import bcrypt

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from fastapi import HTTPException
from app.models.employee import Employee
from app.models.employee_financial import EmployeeFinancialDetail
from app.models.employee_asset import EmployeeAsset
from app.models.payslip import Payslip
 
 
async def get_employee_profile_controller(db: AsyncSession, current_user):

    employee_id = current_user.employee_id

    if not employee_id:
        return {
            "success": False,
            "message": "Employee not linked",
            "data": None
        }

    # =========================================================
    # 🔹 EMPLOYEE (FIXED HERE)
    # =========================================================
    result = await db.execute(
        select(Employee)
        # ❌ removed selectinload(Employee.designation)
        .where(Employee.id == employee_id)
    )
    employee = result.scalar_one_or_none()

    if not employee:
        return {
            "success": False,
            "message": "Employee not found",
            "data": None
        }

    # =========================================================
    # 🔹 FINANCIAL
    # =========================================================
    result = await db.execute(
        select(EmployeeFinancialDetail).where(
            EmployeeFinancialDetail.employee_id == employee_id
        )
    )
    financial = result.scalar_one_or_none()

    # =========================================================
    # 🔹 ASSETS
    # =========================================================
    result = await db.execute(
        select(EmployeeAsset).where(
            EmployeeAsset.employee_id == employee_id
        )
    )
    assets = result.scalars().all()

    # =========================================================
    # 🔹 PAYSLIPS
    # =========================================================
    result = await db.execute(
        select(Payslip).where(
            Payslip.employee_id == employee_id
        )
    )
    payslips = result.scalars().all()

    # =========================================================
    # 🔹 SAFE VALUES
    # =========================================================
    mobile = getattr(employee, "phone_number", None) or getattr(employee, "mobile", None)
    name = getattr(employee, "name", None)
    company_email = getattr(employee, "company_email", None)
    personal_email = getattr(employee, "personal_email", None)
    address = getattr(employee, "address", None)

    designation_name = employee.designation  # ✅ correct usage

    # =========================================================
    # 🔥 FINAL RESPONSE
    # =========================================================
    return {
        "success": True,
        "message": "Employee profile fetched successfully",
        "data": {

            "header": {
                "id": employee.id,
                "employee_code": employee.employee_code,
                "name": name,
                "company_email": company_email,
                "role": designation_name
            },

            "personal": {
                "id": employee.id,
                "employee_code": employee.employee_code,
                "full_name": name,
                "mobile": mobile,
                "role": designation_name,
                "address": address,
                "company_email": company_email,
                "personal_email": personal_email
            },

            "financial": {
                "bank_account": getattr(financial, "bank_account_number", None),
                "bank_name": getattr(financial, "bank_name", None),
                "ifsc_code": getattr(financial, "ifsc_code", None),
                "pan_number": getattr(financial, "pan_number", None),
                "uan_number": getattr(financial, "uan_pf_number", None)
            } if financial else None,

            "assets": [
                {
                    "id": asset.id,
                    "laptop_asset_id": asset.laptop_asset_id,
                    "access_card": asset.access_card,
                    "additional_asset": asset.additional_asset,
                    "status": asset.status,
                    "assigned_at": asset.assigned_at,
                    "returned_at": asset.returned_at,
                    "assigned_reason": asset.assigned_reason,
                    "return_reason": asset.return_reason
                }
                for asset in assets
            ],

            "payslips": [
                {
                    "id": slip.id,
                    "month": slip.month,
                    "file_path": slip.file_path,
                    "uploaded_at": slip.uploaded_at,
                    "year": slip.uploaded_at.year if slip.uploaded_at else None
                }
                for slip in payslips
            ]
        }
    }



# app/controllers/employee_controller.py

async def update_profile(db: AsyncSession, current_user, data):

    employee = current_user.employee

    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    # ❌ nothing provided
    if data.phone_number is None and data.personal_email is None:
        raise HTTPException(
            status_code=400,
            detail="At least one field (phone_number or personal_email) is required"
        )

    # ✅ update mobile
    if data.phone_number is not None:
        phone_number = data.phone_number.strip()

        if not phone_number.isdigit() or len(phone_number) != 10:
            raise HTTPException(status_code=400, detail="Invalid mobile number")

        if phone_number != employee.phone_number:
            employee.phone_number = phone_number

    # ✅ update email
    if data.personal_email is not None:
        if data.personal_email != employee.personal_email:
            employee.personal_email = data.personal_email

    await db.commit()
    await db.refresh(employee)

    return {
        "message": "Profile updated successfully",
        "data": {
            "phone_number": employee.phone_number,
            "personal_email": employee.personal_email
        }
    }

async def change_password(db, current_user, data):

    current_password = data.current_password.strip().encode("utf-8")
    new_password = data.new_password.strip().encode("utf-8")

    # ✅ verify old password
    if not bcrypt.checkpw(current_password, current_user.password.encode("utf-8")):
        raise HTTPException(status_code=400, detail="Current password is incorrect")

    # ✅ hash new password
    hashed_password = bcrypt.hashpw(new_password, bcrypt.gensalt()).decode("utf-8")

    current_user.password = hashed_password
    current_user.token = None   # logout

    await db.commit()
    await db.refresh(current_user)

    return {"message": "Password changed successfully"}