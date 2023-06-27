from app.database.db import Base
from sqlalchemy import Integer, Column, String, Boolean, DateTime


class CheckedDocument(Base):
    __tablename__ = 'checked_document'

    uuid = Column(Integer, primary_key=True, index=True)
    saved_datetime = Column(DateTime)
    vet_document_uuid = Column(String)
    is_mistakes = Column(Boolean)
    person = Column(String)
    description = Column(String)


