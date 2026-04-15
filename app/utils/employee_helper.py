from sqlalchemy import select

from app.models.employee import Employee




# ===============================
# 🔹 GET EMPLOYEE OR 404
# ===============================
async def get_employee_or_404(emp_id, db):

    result = await db.execute(
        select(Employee).where(Employee.id == emp_id)
    )
    employee = result.scalar_one_or_none()

    if not employee:
        return None, {
            "success": False,
            "message": "Employee not found"
        }

    return employee, None


