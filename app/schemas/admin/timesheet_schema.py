from pydantic import BaseModel
from datetime import date, time
from typing import Optional


# 🔹 COMMON STRUCTURES

class EmployeeInfo(BaseModel):
    name: str
    code: str
    designation: str


# 🔹 LATEST ENTRY (UPDATED)

class LatestEntry(BaseModel):
    timesheet_id: Optional[int]   # ✅ ADDED

    date: Optional[date]          # already correct
    day: Optional[str]            # already correct

    check_in: Optional[str]       # already string (12-hour format)
    check_out: Optional[str]

    duration: Optional[str]
    work_update: Optional[str]
    work_status: str
    approval_status: str


# 🔹 LATEST (LIST VIEW)

class LatestTimeSheetResponse(BaseModel):
    employee: EmployeeInfo
    latest_entry: LatestEntry


# 🔹 HISTORY (UPDATED)

class TimeSheetHistoryResponse(BaseModel):
    timesheet_id: int   # ✅ ADDED

    employee_name: str
    employee_code: str
    designation: str

    date: date
    check_in: Optional[time]
    check_out: Optional[time]
    duration: Optional[str]

    work_update: Optional[str] = None
    work_status: str
    approval_status: str
    rejection_reason: Optional[str] = None


# 🔹 ACTION

class TimeSheetActionRequest(BaseModel):
    action: str
    reason: Optional[str] = None