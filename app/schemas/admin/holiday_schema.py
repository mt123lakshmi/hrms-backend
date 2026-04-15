from pydantic import BaseModel
from datetime import date
from enum import Enum


class HolidayType(str, Enum):
    Public = "Public"
    Festival = "Festival"


class HolidayCreate(BaseModel):
    date: date
    type: HolidayType
    name: str
    description: str | None = None


class HolidayResponse(BaseModel):
    id: int
    date: date
    type: HolidayType
    name: str
    description: str | None

    class Config:
        from_attributes = True