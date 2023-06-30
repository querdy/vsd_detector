from sqlalchemy.orm import Mapped, mapped_column

from app.database.db import Base


class Enterprise(Base):
    __tablename__ = 'enterprise'

    uuid: Mapped[int] = mapped_column(primary_key=True, index=True)
    enterprise_guid: Mapped[str] = mapped_column()
    business_entity_guid: Mapped[str] = mapped_column()
