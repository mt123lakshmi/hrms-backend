from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.payslip import Payslip

# ===============================
# 🔹 GET LOGGED-IN EMPLOYEE PAYSLIPS
# ===============================
async def get_my_payslips(db: AsyncSession, user):
    try:
        # 🔒 ENSURE EMPLOYEE LINKED (keep this)
        if not user.employee_id:
            raise HTTPException(status_code=403, detail="Employee not linked")

        result = await db.execute(
            select(Payslip)
            .where(Payslip.employee_id == user.employee_id)
            .order_by(Payslip.uploaded_at.desc())
        )

        payslips = result.scalars().all()

        return {
            "success": True,
            "message": "Payslips fetched successfully",
            "data": [
                {
                    "payslip_id": p.id,
                    "month": p.month,
                    "uploaded_date": p.uploaded_at.date() if p.uploaded_at else None,
                    "file_url": p.file_path
                }
                for p in payslips
            ]
        }

    except HTTPException as e:
        raise e

    except Exception as e:
        return {
            "success": False,
            "message": f"Error fetching payslips: {str(e)}",
            "data": []
        }