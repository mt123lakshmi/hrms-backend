# app/schemas/admin/asset_schema.py

from pydantic import BaseModel
from typing import Optional, Literal

class AssetActionRequest(BaseModel):
    action: Literal["assign", "unassign"]
    employee_id: Optional[int] = None
    reason: str