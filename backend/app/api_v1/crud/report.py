import os

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app import models
from app.api_v1.schema.report import ReportCreateSchema, ReportSchema


async def create_report_db(db: AsyncSession, report: ReportCreateSchema):
    created_report = models.Report(**report.dict())
    db.add(created_report)
    await db.commit()
    return ReportSchema.from_orm(created_report)


async def get_all_reports(db: AsyncSession):
    result = await db.execute(select(models.Report))
    scalar = result.scalars().all()
    response = [ReportSchema.from_orm(item) for item in scalar]
    return response


async def get_report_by_uuid(db: AsyncSession, uuid: int):
    result = await db.execute(select(models.Report))
    scalar = result.scalar()
    return scalar


async def delete_report(db: AsyncSession, file_uuid: int):
    report = await get_report_by_uuid(uuid=file_uuid, db=db)
    await db.execute(delete(models.Report).filter_by(uuid=file_uuid))
    os.remove(report.path[1:])
    await db.commit()
