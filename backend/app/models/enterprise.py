from app.database.db import Base
from sqlalchemy import Integer, Column, String


class Enterprise(Base):
    __tablename__ = 'enterprise'

    uuid = Column(Integer, primary_key=True, index=True)
    enterprise_guid = Column(String)
    business_entity_guid = Column(String)
