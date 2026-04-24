from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os

# ✅ LOAD ENV FILE
load_dotenv()

# ✅ GET DATABASE URL FROM .env
DATABASE_URL = os.getenv("DATABASE_URL")

# 🔥 DEBUG (REMOVE LATER)


# ✅ CREATE ENGINE (ASYNC)
engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    future=True
)

# ✅ SESSION
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# ✅ BASE
Base = declarative_base()

# ✅ DEPENDENCY
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session