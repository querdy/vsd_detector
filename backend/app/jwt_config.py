from pydantic import BaseModel

from app.settings import settings


class JWTSettings(BaseModel):
    authjwt_secret_key: str = settings.SECRET_KEY
    authjwt_access_token_expires: int = settings.ACCESS_TOKEN_EXPIRE_SECONDS
