from sqlalchemy import Column, Integer, String, Boolean, DateTime
from datetime import datetime
from app.database.database import Base
from sqlalchemy import Float

class LeaveType(Base):
    __tablename__ = "leave_type"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(50), unique=True, nullable=False)

    description = Column(String(255), nullable=True)

    max_per_quarter = Column(Float, nullable=True)

    carry_forward = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)