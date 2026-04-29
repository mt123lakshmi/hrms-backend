from pydantic import BaseModel, EmailStr
from typing import Optional


class EmployeeListResponse(BaseModel):
    id: int
    name: str
    company_email: str
    employee_code: str
    designation: str
    role: str


# ===============================
# 🔹 CREATE EMPLOYEE
# ===============================
class CreateEmployeeRequest(BaseModel):
    employee_code: str
    name: str
    phone_number: str
    address: Optional[str] = None
    company_email: str
    personal_email: str

    password: str
    role_id: int

    designation: str

    bank_account: str
    pan_number: str
    uan_number: Optional[str] = None

    # ✅ FIXED — inside class + optional
    access_card: Optional[str] = None
    laptop_id: Optional[str] = None
    assets: Optional[str] = None


# ===============================
# 🔹 UPDATE EMPLOYEE
# ===============================
class UpdateEmployeeRequest(BaseModel):
    employee_code: Optional[str] = None
    name: Optional[str] = None
    phone_number: Optional[str] = None
    address: Optional[str] = None

    company_email: Optional[EmailStr] = None
    personal_email: Optional[EmailStr] = None
    password: Optional[str] = None

    designation: Optional[str] = None

    bank_account: Optional[str] = None
    pan_number: Optional[str] = None
    uan_number: Optional[str] = None

    access_card: Optional[str] = None
    laptop_id: Optional[str] = None
    assets: Optional[str] = None