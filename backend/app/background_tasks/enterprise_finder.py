import asyncio
import datetime

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.api_v1.crud.enterprise import save_enterprise
from app.api_v1.schema.enterprise import EnterpriseSchema
from app.api_v1.schema.ws_message import ProgressMsgSchema, LogMsgSchema, FileMsgSchema, CompleteMsgSchema, \
    PredictionMsgSchema
from app.api_v1.websocket import notifier
from app.services.excel import get_guids_from_excel
from app.settings import settings
from app.vetis import Vetis
from app.vetis.exceptions import VetisNotResultError
from exceptions import GuidNotFoundException


async def backgraund_enterprise_finder(vetis: Vetis, files: list[bytes], db: AsyncSession):
    start_time = datetime.datetime.now()

    for file in files:
        try:
            guids = get_guids_from_excel(file=file)
            guids_lenght = len(guids)
        except GuidNotFoundException:
            continue
        logger.info(f'Обнаружено {len(guids)} guid`ов')
        await notifier.push(str(LogMsgSchema(message=f'Обнаружено {len(guids)} guid`ов')))
        for guid in guids:
            logger.info(f'{guid}')
            if not settings.GUID_PATTERN.fullmatch(guid):
                continue
            try:
                enterprises = await vetis.cerberus.get_activity_location_list(
                    guid=guid
                )
            except VetisNotResultError:
                continue
            for enterprise in enterprises.location:
                await notifier.push(str(FileMsgSchema(message=f"{files.index(file) + 1}/{len(files)}")))
                try:
                    if enterprise.enterprise.address.region.guid != settings.MAIN_REGION_GUID:
                        logger.info(f'ent: {enterprise.enterprise.guid} - находится не в нашем регионе')
                        await notifier.push(str(LogMsgSchema(
                            message=f'ent: {enterprise.enterprise.guid} - находится не в нашем регионе'
                        )))
                        continue
                    logger.info(f'- be: {guid}, ent: {enterprise.enterprise.guid}')
                    await notifier.push(str(LogMsgSchema(message=f'be: {guid}, ent: {enterprise.enterprise.guid}')))
                except AttributeError:
                    continue
                await save_enterprise(
                    db=db,
                    enterprise=EnterpriseSchema(
                        enterprise_guid=enterprise.enterprise.guid,
                        business_entity_guid=guid,
                    )
                )
            await notifier.push(str(ProgressMsgSchema(message=(guids.index(guid) + 1) / guids_lenght * 100)))
            time_spent = datetime.datetime.now() - start_time
            await notifier.push(
                str(PredictionMsgSchema(
                    message=str(
                        time_spent / ((guids.index(guid) + 1) / guids_lenght) - time_spent
                    )
                ))
            )
            await asyncio.sleep(0.01)
    logger.info(f'Сбор завершен')
    await notifier.push(str(LogMsgSchema(message=f'Сбор завершен')))
    await notifier.push(str(CompleteMsgSchema(message=f'Сбор завершен')))
