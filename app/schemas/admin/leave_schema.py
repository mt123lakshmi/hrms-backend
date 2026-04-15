from pydantic import BaseModel, field_validator
from typing import Optional, Literal


class LeaveActionRequest(BaseModel):
    action: Literal["approved", "rejected"]
    rejection_reason: Optional[str] = None

    @field_validator("rejection_reason")
    def validate_rejection_reason(cls, v, values):
        action = values.data.get("action")

        if action == "rejected" and not v:
            raise ValueError("Rejection reason is required when rejecting a leave")

        return v