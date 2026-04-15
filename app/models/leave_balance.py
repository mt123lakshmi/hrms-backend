from sqlalchemy import Column, Integer, ForeignKey, DateTime
from app.database.database import Base
from datetime import datetime
from sqlalchemy.orm import relationship
from sqlalchemy import String


class LeaveBalance(Base):
    __tablename__ = "leave_balances"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"))

    leave_year = Column(Integer)
    total_leaves = Column(Integer)

    casual_leave_total = Column(Integer, default=0)
    casual_leave_used = Column(Integer, default=0)
    casual_leave_remaining = Column(Integer, default=0)

    sick_leave_total = Column(Integer, default=0)
    sick_leave_used = Column(Integer, default=0)
    sick_leave_remaining = Column(Integer, default=0)

    earned_leave_total = Column(Integer, default=0)
    earned_leave_used = Column(Integer, default=0)
    earned_leave_remaining = Column(Integer, default=0)
    last_accrual_quarter = Column(String(10), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)

    employee = relationship("Employee", back_populates="leave_balances")