from pydantic import BaseModel, field_validator
from datetime import date


class CreateLeaveRequest(BaseModel):
    leave_type_id: int
    day_type_id: int 
    start_date: date
    end_date: date
    reason: str

    @field_validator("end_date")
    def validate_dates(cls, v, values):
        start_date = values.data.get("start_date")

        if start_date and v < start_date:
            raise ValueError("End date cannot be before start date")

        return v