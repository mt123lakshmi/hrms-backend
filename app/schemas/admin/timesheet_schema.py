from pydantic import BaseModel
from datetime import date
from typing import Optional, List


# =========================================================
# 🔹 COMMON STRUCTURES
# =========================================================
class EmployeeInfo(BaseModel):
    employee_id: int
    name: str
    code: Optional[str] = None          # ✅ FIX (was str)
    designation: Optional[str] = None   # ✅ FIX (was str)


# =========================================================
# 🔹 LATEST ENTRY (UNCHANGED)
# =========================================================
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


# =========================================================
# 🔹 LATEST (LIST VIEW)
# =========================================================
class LatestTimeSheetResponse(BaseModel):
    employee: EmployeeInfo
    latest_entry: LatestEntry


# =========================================================
# 🔥 HISTORY (NEW STRUCTURE)
# =========================================================

# 🔹 Single history item
class TimeSheetHistoryItem(BaseModel):
    timesheet_id: int

    date: date

    check_in: Optional[str]
    check_out: Optional[str]
    duration: Optional[str]

    work_update: Optional[str] = None
    work_status: str
    approval_status: str
    rejection_reason: Optional[str] = None


# 🔹 Grouped response (MAIN)
class TimeSheetHistoryGroupedResponse(BaseModel):
    employee_id: int
    employee_name: str
    employee_code: Optional[str] = None   # ✅ FIX (was int ❌)
    designation: Optional[str] = None     # ✅ FIX (safe)

    history: List[TimeSheetHistoryItem]


# =========================================================
# 🔹 ACTION
# =========================================================
class TimeSheetActionRequest(BaseModel):
    action: str
    reason: Optional[str] = None