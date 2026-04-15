from sqlalchemy import Column, Integer, DateTime, Date, String, ForeignKey, DECIMAL, Text
from app.database.database import Base
from datetime import datetime

class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"))

    attendance_date = Column(Date)
    check_in_time = Column(DateTime)
    check_out_time = Column(DateTime)

    status = Column(String(50))
    late_entry = Column(Integer, default=0)

    work_hours = Column(DECIMAL(5,2))
    overtime_hours = Column(DECIMAL(5,2))

    remarks = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)