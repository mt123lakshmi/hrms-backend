# app/schemas/admin/payslip_schema.py

from pydantic import BaseModel
from typing import Optional


class PayslipCreateRequest(BaseModel):
    month: str   # example: "February 2026"


class PayslipUpdateRequest(BaseModel):
    month: Optional[str] = None