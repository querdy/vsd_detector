from sqlalchemy.orm import Session, load_only

from app import models
from app.api_v1.schema.enterprise import EnterpriseSchema


def save_enterprise(db: Session, enterprise: EnterpriseSchema):
    if get_enterprise_by_pair(
        db=db,
        enterprise_guid=enterprise.enterprise_guid,
        business_entity_guid=enterprise.business_entity_guid,
    ) is None:
        saved_enterprise = models.Enterprise(**enterprise.dict())
        db.add(saved_enterprise)
        db.commit()


def get_enterprise_by_pair(db: Session, enterprise_guid: str, business_entity_guid: str):
    return db.query(models.Enterprise).filter_by(
        enterprise_guid=enterprise_guid,
        business_entity_guid=business_entity_guid
    ).one_or_none()


def get_enterprises(db: Session):
    return db.query(models.Enterprise).options(load_only(
        models.Enterprise.enterprise_guid,
        models.Enterprise.business_entity_guid)
    ).all()
