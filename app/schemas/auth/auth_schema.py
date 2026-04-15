from pydantic import BaseModel, EmailStr

class LoginRequest(BaseModel):
    company_email: EmailStr
    password: str