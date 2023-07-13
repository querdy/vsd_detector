from pydantic import validator

from app.api_v1.schema.base import CamelModel
from app.api_v1.schema.mixins import ORJSONParserMixin


class UserSchema(CamelModel):
    uuid: str
    login: str
    is_admin: bool

    class Config:
        orm_mode = True


class UserCreateSchema(ORJSONParserMixin, CamelModel):
    login: str
    password: str
    confirm_password: str

    @validator('login')
    def name_must_not_space(cls, login):
        if ' ' in login:
            raise ValueError('В имени не должно быть пробелов.')
        return login

    @validator('confirm_password')
    def passwords_match(cls, c_psw, values):
        if 'password' in values and c_psw != values['password']:
            raise ValueError('Пароли не совпадают.')
        return c_psw


class UserAuthSchema(ORJSONParserMixin, CamelModel):
    login: str
    password: str


class AccessTokenSchema(CamelModel):
    access_token: str


class CurrentUserSchema(CamelModel):
    user: str
    is_admin: bool


class VetisAuthDataSchema(ORJSONParserMixin, CamelModel):
    enterprise_login: str
    enterprise_password: str
    api_key: str
    service_id: str
    issuer_id: str
    initiator: str
