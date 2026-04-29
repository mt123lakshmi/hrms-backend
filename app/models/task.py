from sqlalchemy import Column, Integer, String, Date, Text,ForeignKey
from sqlalchemy.orm import relationship
from app.database.database import Base


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True)

    title = Column(String(255))
    description = Column(Text)

    start_date = Column(Date)
    end_date = Column(Date)
    frequency = Column(String(50))
    company_id = Column(Integer, ForeignKey("company.id"))

    # 🔥 REQUIRED
    worklogs = relationship("WorkLog", back_populates="task")
    company = relationship("Company")