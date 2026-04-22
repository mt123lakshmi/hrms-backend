from pydantic import BaseModel, field_validator
from datetime import date, datetime
from typing import Optional


class TaskCreate(BaseModel):
    employee_id: int
    title: str
    description: str
    start_date: date
    end_date: date
    frequency: Optional[str] = None

    # 🔥 FIX HERE
    @field_validator("start_date", "end_date", mode="before")
    @classmethod
    def parse_date(cls, value):

        if isinstance(value, date):
            return value

        # ✅ support BOTH formats
        formats = ["%m/%d/%Y", "%Y-%m-%d"]

        for fmt in formats:
            try:
                return datetime.strptime(value, fmt).date()
            except:
                continue

        raise ValueError("Invalid date format. Use MM/DD/YYYY or YYYY-MM-DD")