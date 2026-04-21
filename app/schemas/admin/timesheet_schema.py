from pydantic import BaseModel
from datetime import date
from typing import Optional


# 🔹 COMMON STRUCTURES
class EmployeeInfo(BaseModel):
    name: str
    code: str
    designation: str


# 🔹 LATEST ENTRY (UNCHANGED)
class LatestEntry(BaseModel):
    timesheet_id: Optional[int]

    date: Optional[date]
    day: Optional[str]

    check_in: Optional[str]
    check_out: Optional[str]

    duration: Optional[str]
    work_update: Optional[str]
    work_status: str
    approval_status: str


# 🔹 LATEST (LIST VIEW)
class LatestTimeSheetResponse(BaseModel):
    employee: EmployeeInfo
    latest_entry: LatestEntry


# 🔹 HISTORY (FIXED HERE)
class TimeSheetHistoryResponse(BaseModel):
    timesheet_id: int

    employee_name: str
    employee_code: str
    designation: str

    date: date

    check_in: Optional[str]   # ✅ FIXED
    check_out: Optional[str]  # ✅ FIXED

    duration: Optional[str]

    work_update: Optional[str] = None
    work_status: str
    approval_status: str
    rejection_reason: Optional[str] = None


# 🔹 ACTION
class TimeSheetActionRequest(BaseModel):
    action: str
    reason: Optional[str] = None