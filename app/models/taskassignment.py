from sqlalchemy import Column, Integer, ForeignKey, String
from app.database.database import Base

from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
class TaskAssignment(Base):
    __tablename__ = "task_assignments"

    id = Column(Integer, primary_key=True, index=True)

    task_id = Column(Integer, ForeignKey("tasks.id"))
    employee_id = Column(Integer, ForeignKey("employees.id"))

    status = Column(String(50), default="ASSIGNED")
    assigned_at = Column(DateTime, default=datetime.utcnow)