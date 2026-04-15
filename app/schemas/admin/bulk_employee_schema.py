from pydantic import BaseModel, EmailStr


class BulkEmployeeSchema(BaseModel):
    employee_code: str
    name: str
    phone_number: str
    address: str
    company_email: EmailStr
    personal_email: EmailStr
    designation_id: int
    department_id: int
    password: str
    role: str
    bank_account: str
    pan_number: str
    uan_number: str
    access_card: str
    laptop_id: str
    assets: str