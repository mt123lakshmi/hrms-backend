from sqlalchemy import Column, Integer, Date, String, ForeignKey, DateTime, Text, Float
from sqlalchemy.orm import relationship
from app.database.database import Base
from datetime import datetime


class LeaveRequest(Base):
    __tablename__ = "leave_requests"

    id = Column(Integer, primary_key=True, index=True)

    # Employee
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    employee = relationship("Employee", back_populates="leave_requests")

    # Leave type (CL, SL, etc.)
    leave_type_id = Column(Integer, ForeignKey("leave_type.id"), nullable=False)
    leave_type = relationship("LeaveType")

    # Day type (FULL / HALF)
    day_type_id = Column(Integer, ForeignKey("day_type.id"), nullable=False)
    day_type = relationship("DayType")

    # Dates
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)

    # ✅ IMPORTANT: must be FLOAT
    total_days = Column(Float, nullable=False)

    # Reason
    reason = Column(Text, nullable=True)

    # Status
    status = Column(String(20), default="pending")  # pending / approved / rejected

    # Applied date
    applied_date = Column(DateTime, default=datetime.utcnow)

    # Approval
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    approver = relationship("User", foreign_keys=[approved_by])

    approved_at = Column(DateTime, nullable=True)
    rejection_reason = Column(Text, nullable=True)

    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)