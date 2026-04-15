# app/models/payslip.py

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from datetime import datetime
from app.database.database import Base
from sqlalchemy.orm import relationship

class Payslip(Base):
    __tablename__ = "payslips"

    id = Column(Integer, primary_key=True, index=True)

    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)

    month = Column(String(50), nullable=False)        # FIXED
    file_path = Column(String(255), nullable=False)   # FIXED

    uploaded_at = Column(DateTime, default=datetime.utcnow)
    employee = relationship("Employee", back_populates="payslips")