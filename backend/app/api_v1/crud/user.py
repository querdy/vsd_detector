from sqlalchemy.orm import Session

from passlib.hash import pbkdf2_sha256

from app.api_v1.schema.user import UserCreateSchema, UserSchema
from app import models


def create_user(db: Session, user: UserCreateSchema):
    if get_user_by_login(db=db, login=user.login):
        raise ValueError("Пользователь уже существует.")
    created_user = models.User(login=user.login, hashed_password=pbkdf2_sha256.hash(user.password))
    db.add(created_user)
    db.commit()

    return UserSchema.from_orm(created_user)


def get_user_by_login(db: Session, login: str) -> models.User | None:
    return db.query(models.User).filter_by(login=login).one_or_none()


def get_vetis_auth_data_by_user_login(db: Session, login: str) -> models.VetisAuthData | None:
    return db.query(models.VetisAuthData).filter_by(user_login=login).one_or_none()