from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import load_only

from app import models
from app.api_v1.schema.enterprise import EnterpriseSchema


async def save_enterprise(db: AsyncSession, enterprise: EnterpriseSchema):
    if await get_enterprise_by_pair(
        db=db,
        enterprise_guid=enterprise.enterprise_guid,
        business_entity_guid=enterprise.business_entity_guid,
    ) is None:
        saved_enterprise = models.Enterprise(**enterprise.dict())
        db.add(saved_enterprise)
        await db.commit()


async def get_enterprise_by_pair(db: AsyncSession, enterprise_guid: str, business_entity_guid: str):
    result = await db.execute(select(models.Enterprise).filter_by(
        enterprise_guid=enterprise_guid,
        business_entity_guid=business_entity_guid
    ))
    scalar = result.scalar_one_or_none()
    return scalar
    # return db.query(models.Enterprise).filter_by(
    #     enterprise_guid=enterprise_guid,
    #     business_entity_guid=business_entity_guid
    # ).one_or_none()


async def get_enterprises(db: AsyncSession):
    result = await db.execute(select(models.Enterprise).options(load_only(
        models.Enterprise.enterprise_guid,
        models.Enterprise.business_entity_guid)
    ))
    scalar = result.scalars().all()
    return scalar
    # return db.query(models.Enterprise).options(load_only(
    #     models.Enterprise.enterprise_guid,
    #     models.Enterprise.business_entity_guid)
    # ).all()
