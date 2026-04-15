from pydantic import BaseModel
from typing import List,Optional
from datetime import date
 
class EmployeeInfo(BaseModel):
    name: str
    emp_id: str
    role: str
 
 
class HolidaySchema(BaseModel):
    name: str
    date: date
class RecentLeave(BaseModel):
    start_date: date
    end_date: date
    leave_type: str
    reason: str
    status: str
 
    class Config:
        from_attributes = True
 
 
class DashboardData(BaseModel):
    employee: EmployeeInfo
    leave_balance: float
    leaves_taken: float
    pending_requests: int
    next_holiday: Optional[HolidaySchema] = None
    recent_requests: List[RecentLeave]
 
 
class DashboardResponse(BaseModel):
    success: bool
    message: str
    data: DashboardData | None
 