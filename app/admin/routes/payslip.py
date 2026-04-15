from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database import get_db
from app.core.dependencies import admin_required, admin_or_employee
from app.admin.controllers.payslip_controller import *

router = APIRouter(
    prefix="/admin/payslips",
    tags=["Payslips Management"]
)


@router.get("/")
async def get_employees(
    db: AsyncSession = Depends(get_db),
    user=Depends(admin_required)
):
    return await get_employees_with_payslips(db)


@router.get("/{employee_id}")
async def get_payslips(
    employee_id: int,
    db: AsyncSession = Depends(get_db),
    user=Depends(admin_or_employee)
):
    return await get_employee_payslips(employee_id, db, user)


@router.post("/{employee_id}/upload")
async def upload(
    employee_id: int,
    month: str = Form(...),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    user=Depends(admin_required)
):
    return await upload_payslip(employee_id, month, file, db)


@router.put("/{payslip_id}")
async def update(
    payslip_id: int,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    user=Depends(admin_required)
):
    return await update_payslip(payslip_id, file, db)


@router.get("/download/{payslip_id}")
async def download(
    payslip_id: int,
    db: AsyncSession = Depends(get_db),
    user=Depends(admin_or_employee)
):
    return await download_payslip(payslip_id, db, user)