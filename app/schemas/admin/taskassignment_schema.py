from pydantic import BaseModel
from typing import Literal


# =========================================================
# ASSIGN TASK (optional future use)
# =========================================================
class TaskAssign(BaseModel):
    task_id: int
    employee_id: int


# =========================================================
# TASK ASSIGNMENT RESPONSE
# =========================================================
class TaskAssignmentResponse(BaseModel):
    id: int
    task_id: int
    employee_id: int
    status: Literal["ASSIGNED", "IN_PROGRESS", "COMPLETED"]

    class Config:
        from_attributes = True