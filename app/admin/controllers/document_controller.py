import os
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.emp_doctype import DocumentType
from app.models.employee import Employee
from app.models.employee_document import EmployeeDocument
from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import selectinload

UPLOAD_DIR = "uploads/documents"


# ===============================
# 🔹 UPLOAD DOCUMENT (FIXED)
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

    # 🔹 check if document already exists (🔥 MAIN FIX)
    result = await db.execute(
        select(EmployeeDocument).where(
            EmployeeDocument.employee_id == emp_id,
            EmployeeDocument.document_type_id == document_type_id
        )
    )
    existing_doc = result.scalar_one_or_none()

    file_path = None

    # ===============================
    # 🔹 HANDLE FILE
    # ===============================
    if file:
        os.makedirs(UPLOAD_DIR, exist_ok=True)

        unique_name = f"{emp_id}_{document_type_id}_{uuid.uuid4().hex}_{file.filename}"
        file_path = os.path.join(UPLOAD_DIR, unique_name)

        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)

    # ===============================
    # 🔹 UPDATE IF EXISTS
    # ===============================
    if existing_doc:
        # delete old file
        if existing_doc.file_path and os.path.exists(existing_doc.file_path):
            os.remove(existing_doc.file_path)

        existing_doc.file_path = file_path

        await db.commit()
        await db.refresh(existing_doc)

        return {
            "success": True,
            "message": "Document updated",
            "data": {
                "id": existing_doc.id,
                "document_type": doc_type.name,
                "file": existing_doc.file_path
            }
        }

    # ===============================
    # 🔹 CREATE NEW
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
        "message": "Document uploaded" if file else "Document created without file",
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
        .options(selectinload(EmployeeDocument.document_type))
        .where(EmployeeDocument.employee_id == emp_id)
    )

    docs = result.scalars().all()

    return {
        "success": True,
        "data": [
            {
                "id": d.id,
                "document_type_id": d.document_type_id,
                "document_type": d.document_type.name if d.document_type else None,
                "file_path": d.file_path
            }
            for d in docs
        ]
    }


# ===============================
# 🔹 GET DOCUMENT BY ID
# ===============================
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


# ===============================
# 🔹 GET DOCUMENT TYPES
# ===============================
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


# ===============================
# 🔹 CREATE DOCUMENT TYPE
# ===============================
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


# ===============================
# 🔹 UPDATE DOCUMENT (NO CHANGE)
# ===============================
async def update_document_controller(
    db: AsyncSession,
    document_id: int,
    file: UploadFile
):
    result = await db.execute(
        select(EmployeeDocument).where(EmployeeDocument.id == document_id)
    )
    doc = result.scalar_one_or_none()

    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    os.makedirs(UPLOAD_DIR, exist_ok=True)

    unique_name = f"{doc.employee_id}_{doc.document_type_id}_{uuid.uuid4().hex}_{file.filename}"
    file_location = os.path.join(UPLOAD_DIR, unique_name)

    with open(file_location, "wb") as f:
        while chunk := await file.read(1024 * 1024):
            f.write(chunk)

    if doc.file_path and os.path.exists(doc.file_path):
        os.remove(doc.file_path)

    doc.file_path = file_location

    await db.commit()
    await db.refresh(doc)

    return {
        "success": True,
        "message": "File updated successfully",
        "data": {
            "id": doc.id,
            "file_path": doc.file_path
        }
    }