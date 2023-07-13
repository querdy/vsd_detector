import datetime

import pandas
from loguru import logger
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from xlsxwriter import Workbook

from app import models
from app.api_v1.crud.report import create_report_db
from app.api_v1.crud.vet_document import get_mistakes_documents
from app.api_v1.schema.report import ReportCreateSchema
from app.database.db import engine
from app.settings import settings
from exceptions import GuidNotFoundException


async def create_report(db: AsyncSession):
    logger.info('Старт создания отчета')
    start_time = datetime.datetime.now()
    count = await db.scalar(select(func.count()).select_from(models.CheckedDocument).filter_by(is_mistakes=True))

    async def documents_from_db_generator():
        limit = 50000
        for index in range(0, count // limit + 1):
            yield await get_mistakes_documents(db=db, limit=limit, offset=index * limit)

    filename = f'report_{datetime.datetime.now().timestamp()}.xlsx'
    path = f"{settings.REPORT_ROOT}/{filename}"
    '''openpyxl'''
    # wb = Workbook()
    # ws = wb.active
    # async for documents in documents_from_db_generator():
    #     for document in documents:
    #         ws.append(
    #             [document.vet_document_uuid,
    #              document.saved_datetime,
    #              document.person,
    #              document.description]
    #         )
    # wb.save(path)
    # wb.close()
    '''xlsxwriter'''
    wb = Workbook(path, {'constant_memory': True})
    ws = wb.add_worksheet()
    offset = 0
    async for documents in documents_from_db_generator():
        for row in range(len(documents)):
            cols = [documents[row].vet_document_uuid,
                    documents[row].person,
                    documents[row].description]
            for col in range(len(cols)):
                ws.write(row + offset, col, cols[col])
        offset += len(documents)
    wb.close()
    await create_report_db(db=db, report=ReportCreateSchema(path=path, filename=filename))
    logger.info(f'Конец создания отчета - {datetime.datetime.now() - start_time}')


async def create_report_as_pd(db: AsyncSession):
    def _read_sql_query(con, stmt):
        return pandas.read_sql_query(stmt, con)

    logger.info(f'Старт создания отчета')
    start_time = datetime.datetime.now()
    count = await db.scalar(select(func.count()).select_from(models.CheckedDocument).filter_by(is_mistakes=True))
    limit = 50000
    df = pandas.DataFrame()
    for index in range(0, count // limit + 1):
        async with engine.begin() as conn:
            data = await conn.run_sync(_read_sql_query,
                                       select(models.CheckedDocument).filter_by(is_mistakes=True).limit(limit).offset(
                                           index * limit))
            df = pandas.concat([data, df], ignore_index=True)
    filename = f'report_{datetime.datetime.now().timestamp()}.xlsx'
    path = f"{settings.REPORT_ROOT}/{filename}"
    df.to_excel(excel_writer=path, engine='xlsxwriter')
    logger.info(f'Конец создания отчета - {datetime.datetime.now() - start_time}')


def get_guids_from_excel(file: bytes) -> tuple:
    for sheet in range(1, -1, -1):
        try:
            return tuple(
                pandas.read_excel(
                    file, sheet_name=sheet,
                )['Идентификатор в системе (guid)'].to_list()
            )
        except (KeyError, ValueError):
            continue
    raise GuidNotFoundException(f'Ошибка в эксель-файле')
