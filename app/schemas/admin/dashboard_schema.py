from pydantic import BaseModel
from typing import List
from datetime import date
 
 
class PendingLeave(BaseModel):
    employee_name: str
    leave_type: str
    start_date: date
    end_date: date
    reason: str
    status: str
 
 
class DashboardResponse(BaseModel):
    total_employees: int
    leaves_pending: int
    on_leave_today: int
    upcoming_holidays: int
    pending_leaverequest: List[PendingLeave]