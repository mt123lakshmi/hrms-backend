from pydantic import BaseModel, field_validator
from datetime import datetime, date, time
from typing import Optional


class WorkLogCreate(BaseModel):
    task_id: int
    date: date

    check_in: Optional[time] = None
    check_out: Optional[time] = None

    description: str
    proof: Optional[str] = None


    # MM/DD/YYYY → date
    @field_validator("date", mode="before")
    @classmethod
    def parse_date(cls, value):
        if isinstance(value, date):
            return value
        try:
            return datetime.strptime(value, "%m/%d/%Y").date()
        except:
            raise ValueError("Date must be MM/DD/YYYY")


    # 12hr → time
    @field_validator("check_in", "check_out", mode="before")
    @classmethod
    def parse_time(cls, value):
        if not value:
            return None
        try:
            return datetime.strptime(value, "%I:%M %p").time()
        except:
            raise ValueError("Time must be like 09:30 AM")


# ==========================
# RESPONSE
# ==========================
class WorkLogResponse(BaseModel):
    id: int
    task_id: int
    date: str

    check_in: Optional[str]
    check_out: Optional[str]

    description: str
    proof: Optional[str]

    status: str
    rejection_reason: Optional[str]

    class Config:
        from_attributes = True

    @classmethod
    def from_orm_with_format(cls, obj):

        duration = None
        if obj.check_in and obj.check_out:
            delta = datetime.combine(obj.date, obj.check_out) - datetime.combine(obj.date, obj.check_in)
            hours = delta.seconds // 3600
            minutes = (delta.seconds % 3600) // 60
            duration = f"{hours}h {minutes}m"

        status_map = {
            "SUBMITTED": "Pending",
            "APPROVED": "Approved",
            "REJECTED": "Rejected"
        }

        return {
            "id": obj.id,
            "date": obj.date.strftime("%m/%d/%Y"),
            "check_in": obj.check_in.strftime("%I:%M %p") if obj.check_in else None,
            "check_out": obj.check_out.strftime("%I:%M %p") if obj.check_out else None,
            "duration": duration,
            "description": obj.description,
            "proof": obj.proof,
            "status": status_map.get(obj.status, "Unknown"),
            "reason": obj.rejection_reason
        }