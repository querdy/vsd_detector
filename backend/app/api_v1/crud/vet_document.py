from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app import models
from app.api_v1.schema.vet_document import CheckedDocumentSchema


async def save_vet_document(db: AsyncSession, vet_document: CheckedDocumentSchema):
    saved_document = models.CheckedDocument(**vet_document.dict())
    db.add(saved_document)
    await db.commit()


async def get_checked_document_by_vet_document_uuid(db: AsyncSession, vet_document_uuid: str):
    result = await db.execute(select(models.CheckedDocument).filter_by(vet_document_uuid=vet_document_uuid))
    scalar = result.scalar_one_or_none()
    return scalar


async def get_all_checked_document(db: AsyncSession):
    result = await db.execute(select(models.Enterprise))
    scalar = result.scalars().all()
    return scalar


async def get_mistakes_documents(db: AsyncSession, limit: int = None, offset: int = None):
    result = await db.execute(select(models.CheckedDocument).filter_by(is_mistakes=True).limit(limit).offset(offset))
    scalar = result.scalars().all()
    return scalar
