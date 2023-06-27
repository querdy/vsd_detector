from pydantic import BaseModel

from humps.camel import case

from app.api_v1.schema.mixins import ORJSONParserMixin


class CamelModel(BaseModel):
    class Config:
        alias_generator = case
        allow_population_by_field_name = True


class DateIntervalSchema(ORJSONParserMixin, CamelModel):
    date_from: str
    date_to: str
