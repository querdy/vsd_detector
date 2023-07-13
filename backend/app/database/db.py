from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

from app.settings import settings

engine = create_async_engine(settings.DB_STRING, echo=False)
session_local = async_sessionmaker(autocommit=False, autoflush=False, bind=engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


# async def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         await db.close()


async def get_session() -> AsyncSession:
    async with session_local() as session:
        yield session
        