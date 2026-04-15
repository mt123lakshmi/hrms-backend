from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database.database import Base
from datetime import datetime


class EmployeeFinancialDetail(Base):
    __tablename__ = "employee_financial_details"

    id = Column(Integer, primary_key=True, index=True)

    employee_id = Column(Integer, ForeignKey("employees.id"), unique=True)

    bank_account_number = Column(String(50))
    bank_name = Column(String(100))
    ifsc_code = Column(String(20))
    pan_number = Column(String(20))
    uan_pf_number = Column(String(50))

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)

    # 🔥 THIS IS THE MISSING PIECE (YOU MUST HAVE THIS)
    employee = relationship(
        "Employee",
        back_populates="financial_detail"
    )