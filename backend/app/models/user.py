from sqlalchemy import Integer, Column, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from app.database.db import Base


class User(Base):
    __tablename__ = 'user'

    uuid = Column(Integer, primary_key=True, index=True)
    login = Column(String, unique=True)
    hashed_password = Column(String)
    is_admin = Column(Boolean, default=False)
    vetis_auth_data = relationship('VetisAuthData', back_populates='user')


class VetisAuthData(Base):
    __tablename__ = 'vetis_auth_data'

    uuid = Column(Integer, primary_key=True, index=True)
    enterprise_login = Column(String)
    enterprise_password = Column(String)
    api_key = Column(String)
    service_id = Column(String)
    issuer_id = Column(String)
    initiator = Column(String)
    user_login = Column(String, ForeignKey('user.login', ondelete='CASCADE'))
    user = relationship("User", back_populates='vetis_auth_data')
