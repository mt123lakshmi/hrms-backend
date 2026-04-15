from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from app.database.database import Base
from datetime import datetime

class Asset(Base):
    __tablename__ = "assets"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"))

    laptop_asset_id = Column(String(100))
    access_card = Column(String(100))
    additional_asset = Column(Text)

    status = Column(String(50), default="Assigned")

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)