from sqlalchemy import Column, Integer, String, Date, Enum, TIMESTAMP
from sqlalchemy.sql import func
from app.database.database import Base
import enum


class HolidayType(str, enum.Enum):
    PUBLIC = "Public"
    FESTIVAL = "Festival"


class Holiday(Base):
    __tablename__ = "holiday"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False)
    name = Column(String(100), nullable=False)
    type = Column(Enum(HolidayType), nullable=False)
    description = Column(String(255))
    created_at = Column(TIMESTAMP, server_default=func.now())