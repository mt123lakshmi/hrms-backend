from sqlalchemy import Column, Integer, String, Float
from app.database.database import Base

class DayType(Base):
    __tablename__ = "day_type"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(20), nullable=False)
    value = Column(Float, nullable=False)