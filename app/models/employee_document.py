from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database.database import Base
from datetime import datetime

# ✅ import is fine now
from app.models.emp_doctype import DocumentType


class EmployeeDocument(Base):
    __tablename__ = "employee_documents"

    id = Column(Integer, primary_key=True, index=True)

    employee_id = Column(Integer, ForeignKey("employees.id"))
    document_type_id = Column(Integer, ForeignKey("document_types.id"))
   

    file_path = Column(String(255))
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    # relationships
    employee = relationship("Employee", back_populates="documents")
    document_type = relationship("DocumentType", back_populates="documents")