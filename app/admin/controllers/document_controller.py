import os
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.emp_doctype import DocumentType
from app.models.employee import Employee
from app.models.emp_doctype import DocumentType
from app.models.employee_document import EmployeeDocument
from fastapi import HTTPException
from sqlalchemy.orm import selectinload
UPLOAD_DIR = "storage/documents"


# ===============================
# 🔹 UPLOAD DOCUMENT
# ===============================
async def upload_document_controller(emp_id, document_type_id, file, db: AsyncSession):

    # 🔹 check employee
    result = await db.execute(select(Employee).where(Employee.id == emp_id))
    employee = result.scalar_one_or_none()

    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    # 🔹 check document type
    result = await db.execute(
        select(DocumentType).where(DocumentType.id == document_type_id)
    )
    doc_type = result.scalar_one_or_none()

    if not doc_type:
        raise HTTPException(status_code=400, detail="Invalid document type")

    file_path = None  # ✅ important

    # ===============================
    # 🔹 HANDLE FILE (OPTIONAL NOW)
    # ===============================
    if file:
        os.makedirs(UPLOAD_DIR, exist_ok=True)

        unique_name = f"{emp_id}_{document_type_id}_{uuid.uuid4().hex}_{file.filename}"
        file_path = os.path.join(UPLOAD_DIR, unique_name)

        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)

    # ===============================
    # 🔹 SAVE TO DB (WITH OR WITHOUT FILE)
    # ===============================
    doc = EmployeeDocument(
        employee_id=emp_id,
        document_type_id=document_type_id,
        
        file_path=file_path 
    )

    db.add(doc)
    await db.commit()
    await db.refresh(doc)

    return {
        "success": True,
        "message": "Document uploaded" if file else "Document created without file",  # ✅ clear feedback
        "data": {
            "id": doc.id,
            "document_type": doc_type.name,
            "file": doc.file_path
        }
    }
# ===============================
# 🔹 GET DOCUMENTS
# ===============================
async def get_documents_controller(emp_id, db: AsyncSession):

    result = await db.execute(
        select(EmployeeDocument)
        .options(selectinload(EmployeeDocument.document_type))  # ✅ FIX
        .where(EmployeeDocument.employee_id == emp_id)
    )

    docs = result.scalars().all()

    return {
        "success": True,
        "data": [
            {
                "id": d.id,
                "document_type_id": d.document_type_id,
                "document_type": d.document_type.name if d.document_type else None,  # ✅ FIX
                "file_path": d.file_path  # ✅ consistent naming
            }
            for d in docs
        ]
    }

async def get_document_by_id_controller(document_id: int, db: AsyncSession):

    result = await db.execute(
        select(EmployeeDocument)
        .options(selectinload(EmployeeDocument.document_type))
        .where(EmployeeDocument.id == document_id)
    )

    document = result.scalar_one_or_none()

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    return {
        "success": True,
        "data": {
            "id": document.id,
            "employee_id": document.employee_id,
            "document_type_id": document.document_type_id,
            "document_type": document.document_type.name if document.document_type else None,
            "file_path": document.file_path,
            "uploaded_at": document.uploaded_at
        }
    }

async def get_document_types_controller(db: AsyncSession):

    result = await db.execute(select(DocumentType))
    doc_types = result.scalars().all()

    return {
        "success": True,
        "data": [
            {
                "id": dt.id,
                "name": dt.name
            }
            for dt in doc_types
        ]
    }




async def create_document_type(db: AsyncSession, data):

    result = await db.execute(
        select(DocumentType).where(
            DocumentType.name.ilike(data.name)
        )
    )
    existing = result.scalar_one_or_none()

    if existing:
        return {"error": "Document type already exists"}

   
    new_type = DocumentType(name=data.name)

    db.add(new_type)
    await db.commit()
    await db.refresh(new_type)

    return new_type