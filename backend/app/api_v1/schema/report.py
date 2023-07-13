import re

from pydantic import Field, validator

from app.api_v1.schema.base import CamelModel
from app.api_v1.schema.mixins import ORJSONParserMixin
from app.settings import settings


class ReportCreateSchema(CamelModel):
    path: str = Field(alias='url')
    filename: str

    @validator("path")
    def get_path(cls, v, values, **kwargs):
        r = re.sub(f"{settings.REPORT_ROOT}", settings.REPORT_URL, v)
        return r


class ReportSchema(CamelModel):
    uuid: int
    path: str = Field(alias='url')
    filename: str

    class Config:
        orm_mode = True

