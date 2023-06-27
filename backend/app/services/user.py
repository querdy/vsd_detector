from fastapi_jwt_auth import AuthJWT
from passlib.handlers.pbkdf2 import pbkdf2_sha256
from sqlalchemy.orm import Session

from app.api_v1.crud.user import get_user_by_login
from app.api_v1.schema.user import UserSchema, UserAuthSchema


def create_token(user: UserSchema, authorize: AuthJWT):
    return authorize.create_access_token(
        subject=user.login,
        user_claims=user.dict(),
    )


def authenticate(db: Session, user: UserAuthSchema):
    existing_user = get_user_by_login(db=db, login=user.login)
    if existing_user is None:
        raise ValueError("Такого пользователя не существует.")
    elif pbkdf2_sha256.verify(user.password, existing_user.hashed_password):
        return UserSchema.from_orm(existing_user)
    else:
        raise ValueError("Неверный пароль.")
