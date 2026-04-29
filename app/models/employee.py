from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database.database import Base

class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)

    # ✅ OPTIONAL NOW
    employee_code = Column(String(50), unique=True, index=True, nullable=False)

    name = Column(String(100), nullable=False)
    phone_number = Column(String(20), nullable=False)

    # ✅ FIXED NAMING
    profilepic = Column(String(255), nullable=True)

    designation = Column(String(100), nullable=False)

    # ✅ MAKE EXPLICIT (optional or required — your choice)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=True)

    role = relationship("Role", back_populates="employees")

    # ✅ OPTIONAL
    address = Column(String(255), nullable=True)

    company_email = Column(String(120), unique=True, nullable=False)
    personal_email = Column(String(120), nullable=False)

    user = relationship("User", back_populates="employee", uselist=False)

    financial_detail = relationship(
        "EmployeeFinancialDetail",
        back_populates="employee",
        uselist=False
    )

    assets = relationship("EmployeeAsset", back_populates="employee")
    documents = relationship("EmployeeDocument", back_populates="employee")
    payslips = relationship("Payslip", back_populates="employee")

    leave_balances = relationship(
        "LeaveBalance",
        back_populates="employee",
        cascade="all, delete"
    )

    leave_requests = relationship(
        "LeaveRequest",
        back_populates="employee",
        cascade="all, delete"
    )

    company_id = Column(Integer, ForeignKey("company.id"), nullable=False)