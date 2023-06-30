from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from passlib.hash import pbkdf2_sha256

from app.api_v1.schema.user import UserCreateSchema, UserSchema
from app import models


async def create_user(db: AsyncSession, user: UserCreateSchema):
    if await get_user_by_login(db=db, login=user.login):
        raise ValueError("Пользователь уже существует.")
    created_user = models.User(login=user.login, hashed_password=pbkdf2_sha256.hash(user.password))
    db.add(created_user)
    await db.commit()
    return UserSchema.from_orm(created_user)


async def get_user_by_login(db: AsyncSession, login: str) -> models.User | None:
    result = await db.execute(select(models.User).filter_by(login=login))
    scalar = result.scalar_one_or_none()
    return scalar


async def get_vetis_auth_data_by_user_login(db: AsyncSession, login: str) -> models.VetisAuthData | None:
    result = await db.execute(select(models.VetisAuthData).filter_by(user_login=login))
    scalar = result.scalar_one_or_none()
    return scalar
