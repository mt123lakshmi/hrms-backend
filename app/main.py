from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from fastapi.staticfiles import StaticFiles
 
# 🔹 Database
from app.database.database import Base, engine
 
# 🔹 Init
from app.core.init_db import create_admin
 
# 🔹 Import ALL models (REQUIRED for table creation)
from app.models.user import User
from app.models.employee import Employee
from app.auth.routes import auth_routes

from app.models.attendance import Attendance
from app.models.leave_type import LeaveType
from app.models.leave_request import LeaveRequest
from app.models.leave_balance import LeaveBalance
from app.models.holiday import Holiday
from app.models.asset import Asset
from app.models.employee_asset import EmployeeAsset
from app.models.employee_financial import EmployeeFinancialDetail
from app.models.employee_document import EmployeeDocument
from app.models.payslip import Payslip
from app.models.day_type import DayType
# 🔹 Import routes
from app.auth.routes import auth_routes

 
# 🔥 ADMIN ROUTES
from app.admin.routes import dashboard as admin_dashboard
from app.admin.routes import master_route
from app.admin.routes import employee as admin_employee
from app.admin.routes import document
from app.admin.routes import leave
from app.admin.routes import attendance
from app.admin.routes import holiday
from app.admin.routes import asset
from app.admin.routes import payslip
from app.admin.routes.role import router as role_router
# 🔥 EMPLOYEE ROUTES
from app.employee.routes import emp_dashboard
from app.employee.routes import profile
from app.employee.routes import emp_leave
from app.employee.routes import emp_attendance
from app.employee.routes.emppayslip_route import router as emp_payslip_router
from app.jobs.leave_accrual import start_scheduler

from app.auth.routes import password
# ==========================
# 🔥 INIT APP
# ==========================
app = FastAPI(
    title="HRMS Backend",
    version="1.0.0"
)
 
# 🔹 Security
security = HTTPBearer()
 
# ==========================
# 🔥 CORS CONFIG
# ==========================
origins = [
  "*",
]
 
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
 
# ==========================
# 🔥 STATIC FILES
# ==========================
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
 
# ==========================
# 🔹 STARTUP EVENT
# ==========================
@app.on_event("startup")
async def startup_event():
    print("🚀 Starting application...")
 
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
 
    print("✅ Tables created")
 
    # Create admin user
    await create_admin()
 
    print("✅ Admin check completed")
 
 
# ==========================
# 🔐 AUTH ROUTES
# ==========================
app.include_router(auth_routes.router)
app.include_router(password.router)
 
# ==========================
# 👑 ADMIN ROUTES
# ==========================
app.include_router(admin_dashboard.router)
app.include_router(master_route.router)
app.include_router(admin_employee.router)
app.include_router(document.router)
app.include_router(leave.router)
app.include_router(attendance.router)
app.include_router(holiday.router)
app.include_router(asset.router)
app.include_router(payslip.router)
app.include_router(role_router)
# ==========================
# 👨‍💻 EMPLOYEE ROUTES
# ==========================
app.include_router(emp_dashboard.router)
app.include_router(profile.router)
app.include_router(emp_leave.router)
app.include_router(emp_attendance.router)
app.include_router(emp_payslip_router)
# ==========================
# 🔹 ROOT
# ==========================
@app.get("/")
async def root():
    return {
        "success": True,
        "message": "HRMS API is running"
    }
 