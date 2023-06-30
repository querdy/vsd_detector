from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.database.db import Base


class User(Base):
    __tablename__ = 'user'

    uuid: Mapped[int] = mapped_column(primary_key=True, index=True)
    login: Mapped[str] = mapped_column(unique=True)
    hashed_password: Mapped[str] = mapped_column()
    is_admin: Mapped[bool] = mapped_column(default=False)
    vetis_auth_data = relationship('VetisAuthData', back_populates='user')


class VetisAuthData(Base):
    __tablename__ = 'vetis_auth_data'

    uuid: Mapped[int] = mapped_column(primary_key=True, index=True)
    enterprise_login: Mapped[str] = mapped_column()
    enterprise_password: Mapped[str] = mapped_column()
    api_key: Mapped[str] = mapped_column()
    service_id: Mapped[str] = mapped_column()
    issuer_id: Mapped[str] = mapped_column()
    initiator: Mapped[str] = mapped_column()
    user_login: Mapped[str] = mapped_column(ForeignKey('user.login', ondelete='CASCADE'))
    user = relationship("User", back_populates='vetis_auth_data')
