import datetime

from sqlalchemy.orm import Mapped, mapped_column

from app.database.db import Base


class CheckedDocument(Base):
    __tablename__ = 'checked_document'

    uuid: Mapped[int] = mapped_column(primary_key=True, index=True)
    saved_datetime: Mapped[datetime.datetime] = mapped_column()
    vet_document_uuid: Mapped[str] = mapped_column(unique=True)
    is_mistakes: Mapped[bool] = mapped_column()
    person: Mapped[str] = mapped_column()
    description: Mapped[str] = mapped_column()


