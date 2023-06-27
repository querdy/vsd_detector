import datetime

from app.api_v1.schema.base import CamelModel


class CheckedDocumentSchema(CamelModel):
    vet_document_uuid: str
    saved_datetime: datetime.datetime
    is_mistakes: bool
    person: str | None
    description: str | None

    class Config:
        orm_mode = True
