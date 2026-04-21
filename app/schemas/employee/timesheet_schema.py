from pydantic import BaseModel, validator, model_validator
from datetime import datetime, date, time
from typing import Optional


class TimeSheetCreate(BaseModel):
    date: date
    check_in: Optional[time] = None
    check_out: Optional[time] = None
    work_update: Optional[str] = None

    # ✅ DATE FORMAT
    @validator("date", pre=True)
    def parse_date(cls, v):
        if isinstance(v, date):
            return v

        for fmt in ("%m/%d/%Y", "%Y-%m-%d"):
            try:
                return datetime.strptime(v, fmt).date()
            except:
                continue

        raise ValueError("Date must be MM/DD/YYYY or YYYY-MM-DD")

    # ✅ TIME PARSER
    @validator("check_in", "check_out", pre=True)
    def parse_time(cls, v):
        if not v:
            return None

        if isinstance(v, time):
            return v

        v = v.strip()

        # 12-hour format
        try:
            return datetime.strptime(v, "%I:%M %p").time()
        except:
            pass

        # ISO format
        try:
            return datetime.fromisoformat(v.replace("Z", "")).time()
        except:
            raise ValueError("Time must be HH:MM AM/PM (e.g. 06:30 PM)")

    # ✅ CHECK-OUT VALIDATION
    @validator("check_out")
    def validate_checkout(cls, v, values):
        check_in = values.get("check_in")
        date_val = values.get("date")

        if v and check_in and date_val:
            check_in_dt = datetime.combine(date_val, check_in)
            check_out_dt = datetime.combine(date_val, v)

            if check_out_dt <= check_in_dt:
                raise ValueError("Check-out must be after check-in")

        return v

    # 🔥 FIXED FOR PYDANTIC V2
    @model_validator(mode="after")
    def validate_at_least_one_field(self):
        if not (self.check_in or self.check_out or self.work_update):
            raise ValueError(
                "Provide at least one field (check_in, check_out, work_update)"
            )
        return self

class TimeSheetResponse(BaseModel):
    id: int
    date: date

    # ✅ NOW STRING
    check_in: Optional[str]
    check_out: Optional[str]

    duration: Optional[str]
    work_update: Optional[str]
    approval_status: str
    rejection_reason: Optional[str]

    class Config:
        orm_mode = True