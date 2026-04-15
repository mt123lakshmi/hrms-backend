from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database.database import Base


class DocumentType(Base):
    __tablename__ = "document_types"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)

    # optional reverse relationship
    documents = relationship("EmployeeDocument", back_populates="document_type")