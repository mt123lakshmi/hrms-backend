# app/models/employee_asset.py

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.database.database import Base


class EmployeeAsset(Base):
    __tablename__ = "employee_assets"

    id = Column(Integer, primary_key=True)

    employee_id = Column(Integer, ForeignKey("employees.id"))

    # 🔥 FIXED (ADD LENGTH)
    laptop_asset_id = Column(String(100))
    access_card = Column(String(100))
    additional_asset = Column(String(255))

    status = Column(String(50), default="assigned")

    assigned_reason = Column(String(255))
    return_reason = Column(String(255))

    assigned_at = Column(DateTime)
    returned_at = Column(DateTime)

    employee = relationship("Employee", back_populates="assets")