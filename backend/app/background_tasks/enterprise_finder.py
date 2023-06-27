import asyncio

from loguru import logger
from sqlalchemy.orm import Session
from zeep.exceptions import XMLParseError

from app.api_v1.crud.enterprise import save_enterprise
from app.api_v1.schema.enterprise import EnterpriseSchema
from app.api_v1.schema.ws_message import ProgressMsgSchema, LogMsgSchema
from app.api_v1.websocket import notifier
from app.vetis import Vetis


async def backgraund_enterprise_finder(vetis: Vetis, guids: tuple, db: Session):
    for guid in guids:
        logger.info(f'- {guid}')
        try:
            enterprises = await vetis.cerberus.get_activity_location_list(
                guid=guid
            )
            # logger.info(f'{enterprises}')
        except XMLParseError:
            logger.info(f'Не удалось получить площадки для предприятия {guid}')
            continue
        if enterprises is None:
            continue
        for enterprise in enterprises.location:
            logger.info(f'- be: {guid}, ent: {enterprise.enterprise.guid}')
            await notifier.push(str(LogMsgSchema(message=f'be: {guid}, ent: {enterprise.enterprise.guid}')))
            try:
                if enterprise.enterprise.address.region.guid != '4f8b1a21-e4bb-422f-9087-d3cbf4bebc14':
                    await notifier.push(str(LogMsgSchema(
                        message=f'ent: {enterprise.enterprise.guid} - находится не в нашем регионе'
                    )))
                    continue
            except AttributeError:
                continue
            save_enterprise(
                db=db,
                enterprise=EnterpriseSchema(
                    enterprise_guid=enterprise.enterprise.guid,
                    business_entity_guid=guid,
                )
            )
            await asyncio.sleep(0.01)
        await notifier.push(str(ProgressMsgSchema(message=(guids.index(guid) + 1) / len(guids) * 100)))
        await asyncio.sleep(0.01)
