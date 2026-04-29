import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, UploadFile

from app.models.emp_doctype import DocumentType
from app.models.employee import Employee
from app.models.employee_document import EmployeeDocument

from app.utils.s3bucket import upload_file_to_s3
from app.utils.s3bucket import (
    extract_s3_key,
    generate_presigned_download_url
)

# ===============================
# 🔹 COMMON FILE UPLOAD HELPER
# ===============================
async def handle_s3_upload(file: UploadFile, emp_id: int, document_type_id: int):
    if not file:
        raise HTTPException(status_code=400, detail="File is required")

    file_bytes = await file.read()

    if not file_bytes:
        raise HTTPException(status_code=400, detail="Empty file uploaded")

    content_type = file.content_type or "application/octet-stream"

    unique_name = f"{emp_id}_{document_type_id}_{uuid.uuid4().hex}_{file.filename}"
    s3_key = f"employee-documents/{unique_name}"

    return upload_file_to_s3(file_bytes, s3_key, content_type)


# ===============================
# 🔹 UPLOAD DOCUMENT
# ===============================
async def upload_document_controller(
    emp_id: int,
    document_type_id: int,
    file: UploadFile,
    db: AsyncSession,
    user   # ✅ ADDED ONLY THIS
):

    # 🔥 COMPANY VALIDATION (ADDED)
    result = await db.execute(
        select(Employee).where(
            Employee.id == emp_id,
            Employee.company_id == user.company_id
        )
    )
    employee = result.scalar_one_or_none()

    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    # check document type
    result = await db.execute(
        select(DocumentType).where(DocumentType.id == document_type_id)
    )
    doc_type = result.scalar_one_or_none()

    if not doc_type:
        raise HTTPException(status_code=400, detail="Invalid document type")

    # check existing document
    result = await db.execute(
        select(EmployeeDocument).where(
            EmployeeDocument.employee_id == emp_id,
            EmployeeDocument.document_type_id == document_type_id
        )
    )
    existing_doc = result.scalar_one_or_none()

    file_url = await handle_s3_upload(file, emp_id, document_type_id)

    if existing_doc:
        existing_doc.file_path = file_url

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

    doc = EmployeeDocument(
        employee_id=emp_id,
        document_type_id=document_type_id,
        file_path=file_url
    )

    db.add(doc)
    await db.commit()
    await db.refresh(doc)

    return {
        "success": True,
        "message": "Document uploaded",
        "data": {
            "id": doc.id,
            "document_type": doc_type.name,
            "file": doc.file_path
        }
    }


# ===============================
# 🔹 UPDATE DOCUMENT
# ===============================
async def update_document_controller(
    db: AsyncSession,
    document_id: int,
    file: UploadFile,
    user   # ✅ ADDED
):
    if not file:
        raise HTTPException(status_code=400, detail="File is required")

    # 🔥 COMPANY VALIDATION (ADDED)
    result = await db.execute(
        select(EmployeeDocument)
        .join(Employee)
        .where(
            EmployeeDocument.id == document_id,
            Employee.company_id == user.company_id
        )
    )
    doc = result.scalar_one_or_none()

    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    file_url = await handle_s3_upload(
        file,
        doc.employee_id,
        doc.document_type_id
    )

    doc.file_path = file_url

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


# ===============================
# 🔹 GET DOCUMENTS
# ===============================
async def get_documents_controller(emp_id: int, db: AsyncSession, user):  # ✅ ADDED

    # 🔥 COMPANY VALIDATION (ADDED)
    emp_check = await db.execute(
        select(Employee).where(
            Employee.id == emp_id,
            Employee.company_id == user.company_id
        )
    )
    if not emp_check.scalar_one_or_none():
        raise HTTPException(404, "Employee not found")

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
async def get_document_by_id_controller(document_id: int, db: AsyncSession, user):  # ✅ ADDED

    result = await db.execute(
        select(EmployeeDocument)
        .join(Employee)
        .options(selectinload(EmployeeDocument.document_type))
        .where(
            EmployeeDocument.id == document_id,
            Employee.company_id == user.company_id
        )
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
            {"id": dt.id, "name": dt.name}
            for dt in doc_types
        ]
    }


# ===============================
# 🔹 CREATE DOCUMENT TYPE
# ===============================
async def create_document_type(db: AsyncSession, data):

    result = await db.execute(
        select(DocumentType).where(DocumentType.name.ilike(data.name))
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
# 🔹 DOWNLOAD DOCUMENT
# ===============================
async def download_document_controller(document_id: int, db, user):  # ✅ ADDED

    result = await db.execute(
        select(EmployeeDocument)
        .join(Employee)
        .where(
            EmployeeDocument.id == document_id,
            Employee.company_id == user.company_id
        )
    )
    doc = result.scalar_one_or_none()

    if not doc:
        raise HTTPException(404, "Document not found")

    return {
        "success": True,
        "download_url": doc.file_path
    }