from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database.database import Base

class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    employee_code = Column(String(50), unique=True, index=True, nullable=False)

    name = Column(String(100))
    phone_number = Column(String(20))
    photo = Column(String(255), nullable=True)

    designation = Column(String(100))
    
    role_id = Column(Integer, ForeignKey("roles.id"))

    role = relationship("Role", back_populates="employees")
    
    

    address = Column(String(255))

    company_email = Column(String(120), unique=True)
    personal_email = Column(String(120))

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

    # ✅ ADD THIS
    leave_requests = relationship(
    "LeaveRequest",
    back_populates="employee",
    cascade="all, delete"
   )