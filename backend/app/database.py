from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine,AsyncSession
from dotenv import load_dotenv
load_dotenv()
import os

SQLALCHEMY_URL=f"postgresql+asyncpg://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}"
print("DB URL =", SQLALCHEMY_URL)
engine=create_async_engine(SQLALCHEMY_URL)
SessionLocal=sessionmaker(autoflush=False,class_=AsyncSession,expire_on_commit=False,autocommit=False,bind=engine)

async def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        await db.close()