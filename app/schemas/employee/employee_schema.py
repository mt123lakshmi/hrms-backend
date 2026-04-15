from typing import Optional
from pydantic import BaseModel, EmailStr

class UpdateProfileRequest(BaseModel):
    phone_number: Optional[str] = None
    personal_email: Optional[EmailStr] = None


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str