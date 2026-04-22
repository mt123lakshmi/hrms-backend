from sqlalchemy import Column, Integer, String, Date, Time, ForeignKey
from sqlalchemy.orm import relationship
from app.database.database import Base


class WorkLog(Base):
    __tablename__ = "work_logs"

    id = Column(Integer, primary_key=True, index=True)

    employee_id = Column(Integer, ForeignKey("employees.id"))
    task_id = Column(Integer, ForeignKey("tasks.id"))

    date = Column(Date)

    check_in = Column(Time, nullable=True)
    check_out = Column(Time, nullable=True)

    description = Column(String)
    proof = Column(String, nullable=True)

    status = Column(String, default="SUBMITTED")
    rejection_reason = Column(String, nullable=True)

    # ✅ FIX (you missed this earlier)
    task = relationship("Task")
    employee = relationship("Employee")