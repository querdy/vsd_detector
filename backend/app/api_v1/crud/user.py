from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from passlib.hash import pbkdf2_sha256

from app.api_v1.schema.user import UserCreateSchema, VetisAuthDataSchema
from app import models


async def create_user(db: AsyncSession, user: UserCreateSchema):
    if await get_user_by_login(db=db, login=user.login):
        raise ValueError("Пользователь уже существует.")
    created_user = models.User(login=user.login, hashed_password=pbkdf2_sha256.hash(user.password))
    db.add(created_user)
    await db.commit()


async def get_user_by_login(db: AsyncSession, login: str) -> models.User | None:
    result = await db.execute(select(models.User).filter_by(login=login))
    scalar = result.scalar_one_or_none()
    return scalar


async def get_vetis_auth_data_by_user_login(db: AsyncSession, login: str) -> models.VetisAuthData | None:
    result = await db.execute(select(models.VetisAuthData).filter_by(user_login=login))
    scalar = result.scalar_one_or_none()
    return scalar


async def save_vetis_auth_data_for_user(db: AsyncSession, vetis: VetisAuthDataSchema, user: models.User):
    vetis_auth_data_in_db = await get_vetis_auth_data_by_user_login(db=db, login=user.login)
    if vetis_auth_data_in_db is None:
        create_vetis_auth_data = models.VetisAuthData(**vetis.dict(), user_login=user.login, user=user)
        db.add(create_vetis_auth_data)
    else:
        values = {key: value for key, value in vetis.dict().items() if value}
        await db.execute(update(models.VetisAuthData).filter_by(user_login=user.login).values(**values))
    await db.commit()
