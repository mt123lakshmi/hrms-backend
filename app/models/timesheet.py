from sqlalchemy import Column, Integer, String, Time, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.database.database import Base

class TimeSheet(Base):
    __tablename__ = "timesheet"

    id = Column(Integer, primary_key=True, index=True)

    employee_id = Column(Integer, ForeignKey("employees.id"))

    date = Column(Date, nullable=False)

    check_in = Column(Time, nullable=True)
    check_out = Column(Time, nullable=True)

    duration = Column(String(20), nullable=True)  # ✅ ADDED

    work_update = Column(String(500))

    work_status = Column(String(50), default="Pending")

    approval_status = Column(String(50), default="Pending")
    rejection_reason = Column(String(500), nullable=True)

    employee = relationship("Employee", backref="timesheets")