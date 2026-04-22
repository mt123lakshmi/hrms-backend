from sqlalchemy import Column, Integer, String, Date, Text
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

    # 🔥 REQUIRED
    worklogs = relationship("WorkLog", back_populates="task")