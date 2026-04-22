from pydantic import BaseModel
from datetime import date
from typing import Optional


class WorkLogResponse(BaseModel):
    id: int
    date: date
    check_in: Optional[str]
    check_out: Optional[str]
    duration: Optional[str]
    description: str
    proof: Optional[str]
    status: str
    rejection_reason: Optional[str]

    class Config:
        from_attributes = True