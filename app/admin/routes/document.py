from fastapi import APIRouter, UploadFile, File, Form, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.database.database import get_db
from app.core.dependencies import admin_required
from app.schemas.admin.document_type_schema import DocumentTypeCreate

from app.admin.controllers.document_controller import (
    upload_document_controller,
    get_documents_controller,
    get_document_by_id_controller,
    get_document_types_controller,
    create_document_type
)

router = APIRouter(prefix="/documents", tags=["Documents"])


# 🔥 ADMIN ONLY
@router.post("/employee/{emp_id}")
async def upload_document(
    emp_id: int,
    document_type_id: int = Form(...),
    file: Optional[UploadFile] = File(None),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(admin_required)
):
    return await upload_document_controller(emp_id, document_type_id, file, db)


# 🔥 ADMIN ONLY
@router.get("/employee/{emp_id}")
async def get_documents(
    emp_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(admin_required)  # 🔥 enforce admin
):
    return await get_documents_controller(emp_id, db)

@router.get("/types")
async def get_document_types(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(admin_required)  # optional
):
    return await get_document_types_controller(db)


@router.get("/{document_id}")
async def get_document_by_id(
    document_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(admin_required)
):
    return await get_document_by_id_controller(document_id, db)


@router.post("/create")
async def create_document_type_api(
    data: DocumentTypeCreate,
    db: AsyncSession = Depends(get_db)
):
    return await create_document_type(db, data)