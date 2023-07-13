from sqlalchemy.orm import Mapped, mapped_column

from app.database.db import Base


class Report(Base):
    __tablename__ = 'report'

    uuid: Mapped[int] = mapped_column(primary_key=True, index=True)
    path: Mapped[str] = mapped_column(default=None)
    filename: Mapped[str] = mapped_column()
