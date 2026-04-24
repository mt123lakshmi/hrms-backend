from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.payslip import Payslip
from app.utils.s3bucket import extract_s3_key, generate_presigned_download_url

async def get_my_payslips(db: AsyncSession, user):

    if not user.employee_id:
        raise HTTPException(status_code=403, detail="Employee not linked")

    result = await db.execute(
        select(Payslip)
        .where(Payslip.employee_id == user.employee_id)
        .order_by(Payslip.uploaded_at.desc())
    )

    payslips = result.scalars().all()

    data = []

    for p in payslips:
        file_url = p.file_path  # direct S3 (VIEW)
        
        # 🔥 generate download URL
        key = extract_s3_key(file_url)
        download_url = generate_presigned_download_url(key)

        data.append({
            "payslip_id": p.id,
            "month": p.month,
            "uploaded_date": p.uploaded_at.date() if p.uploaded_at else None,
            "view_url": file_url,
            "download_url": download_url
        })

    return {
        "success": True,
        "message": "Payslips fetched successfully",
        "data": data
    }