from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.database.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    company_email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)

    role_id = Column(Integer, ForeignKey("roles.id"))
    role = relationship("Role", lazy="selectin")

    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    employee = relationship("Employee", back_populates="user", lazy="selectin")

    # 🔥 ADD THESE (CRITICAL)
    otp = Column(String(10), nullable=True)
    otp_expiry = Column(DateTime, nullable=True)