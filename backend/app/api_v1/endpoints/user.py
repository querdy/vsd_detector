from fastapi import APIRouter, Depends, Form
from fastapi_jwt_auth import AuthJWT
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.responses import JSONResponse

from app import models
from app.api_v1.crud.user import create_user
from app.api_v1.schema.user import UserSchema, UserCreateSchema, UserAuthSchema, AccessTokenSchema, CurrentUserSchema
from app.database.db import get_db
from app.services.user import create_token, authenticate

router = APIRouter(prefix="/user")


@router.post('/register', status_code=status.HTTP_201_CREATED, response_model=AccessTokenSchema)
async def register_new_user(user: UserCreateSchema = Form(), authorize: AuthJWT = Depends(), db: AsyncSession = Depends(get_db)):
    try:
        created_user: models.User = await create_user(db, user)
        token = create_token(created_user, authorize)
        return {'access_token': token}
    except Exception as err:
        return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content={"detail": str(err)})


@router.post('/login', status_code=status.HTTP_200_OK, response_model=AccessTokenSchema)
async def authenticate_user(user: UserAuthSchema = Form(), authorize: AuthJWT = Depends(), db: AsyncSession = Depends(get_db)):
    try:
        existing_user: UserSchema = await authenticate(db, user)
        token = create_token(existing_user, authorize)
        return {'access_token': token}

    except Exception as err:
        return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={"detail": str(err)})


@router.get("/me", status_code=status.HTTP_200_OK)
async def get_user(authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    current_user = authorize.get_jwt_subject()
    is_admin = authorize.get_raw_jwt()["is_admin"]
    return {"user": current_user, "is_admin": is_admin}



