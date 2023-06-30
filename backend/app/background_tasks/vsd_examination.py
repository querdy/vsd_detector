import asyncio
import datetime
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from zeep.exceptions import XMLParseError

from app.api_v1.crud.enterprise import get_enterprises, save_enterprise
from app.api_v1.schema.enterprise import EnterpriseSchema
from app.api_v1.schema.ws_message import LogMsgSchema, ProgressMsgSchema
from app.api_v1.websocket import notifier
from app.services.vetis import Validator
from app.vetis import Vetis
from app.vetis.clients.mercury import VetisBadServerError, VetisRejectedError


async def get_vet_documents(
        vetis: Vetis,
        be_guid: str,
        enterprise_guid: str,
        begin_date: str,
        end_date: str):

    total_vsd = 0
    offset = 0
    while True:
        if offset > total_vsd:
            raise StopIteration
        await vetis.mercury.get_vet_document_changes_list(
            owner_guid=be_guid,
            enterprise_guid=enterprise_guid,
            begin_date=datetime.datetime.strptime(begin_date, '%Y-%m-%d'),
            end_date=datetime.datetime.strptime(end_date, '%Y-%m-%d'),
            offset=offset,
        )
        try:
            response = await vetis.mercury.get_finished_response()
            total_vsd = response.result._value_1.vetDocumentList.total
            offset += 500
            vet_documents = response.result._value_1.vetDocumentList.vetDocument
            yield vet_documents
        except (VetisBadServerError, VetisRejectedError):
            offset += 500
            yield []


async def backgraund_vsd_examination(
        vetis: Vetis,
        begin_date: str,
        end_date: str,
        db: AsyncSession,
        be_guids: tuple | None = None):
    if not be_guids:
        enterprises = await get_enterprises(db=db)
        enterprises_length = len(enterprises)
        for enterprise in enterprises:
            vet_documents_generator = get_vet_documents(
                vetis=vetis,
                be_guid=enterprise.business_entity_guid,
                enterprise_guid=enterprise.enterprise_guid,
                begin_date=begin_date,
                end_date=end_date,
            )
            try:
                while True:
                    vet_documents = await anext(vet_documents_generator)
                    for vet_document in vet_documents:
                        logger.info(f'vsd: {vet_document.uuid}')
                        if vet_document.vetDStatus != 'WITHDRAWN':
                            await Validator(vet_document, vetis, db=db).run()
                            await asyncio.sleep(0.01)
                    await notifier.push(
                        str(ProgressMsgSchema(message=(enterprises.index(enterprise) + 1) / enterprises_length * 100)))
                    await asyncio.sleep(0.01)
            except RuntimeError:
                continue
    else:
        be_guids_length = len(be_guids)
        for guid in be_guids:
            logger.info(f'- {guid}')
            try:
                enterprises = await vetis.cerberus.get_activity_location_list(guid=guid)
            except XMLParseError:
                logger.info(f'Не удалось получить площадки для предприятия {guid}')
                continue
            if enterprises is None:
                continue
            for enterprise in enterprises.location:
                if enterprise.enterprise.address.region.guid != '4f8b1a21-e4bb-422f-9087-d3cbf4bebc14':
                    continue
                await save_enterprise(
                    db=db,
                    enterprise=EnterpriseSchema(
                        enterprise_guid=enterprise.enterprise.guid,
                        business_entity_guid=guid,
                    )
                )
                vet_documents_generator = get_vet_documents(
                    vetis=vetis,
                    be_guid=guid,
                    enterprise_guid=enterprise.enterprise.guid,
                    begin_date=begin_date,
                    end_date=end_date,
                )
                try:
                    while True:
                        vet_documents = await anext(vet_documents_generator)
                        for vet_document in vet_documents:
                            logger.info(f'vsd: {vet_document.uuid}')
                            if vet_document.vetDStatus != 'WITHDRAWN':
                                await Validator(vet_document, vetis, db=db).run()
                                await asyncio.sleep(0.01)
                        await notifier.push(
                            str(ProgressMsgSchema(
                                message=(be_guids.index(guid) + 1) / be_guids_length * 100)))
                        await asyncio.sleep(0.01)
                except RuntimeError:
                    continue

    logger.info(f'Проверка завершена')
    await notifier.push(str(LogMsgSchema(message=f'Проверка завершена')))

# async def backgraund_vsd_examination(
#         vetis: Vetis,
#         begin_date: str,
#         end_date: str,
#         db: Session,
#         be_guids: tuple | None = None):
#     if not be_guids:
#         enterprises = tuple(get_enterprises(db=db))
#         enterprises_length = len(enterprises)
#         for enterprise in enterprises:
#             vet_documents = await get_all_vet_document(
#                 vetis=vetis,
#                 be_guid=enterprise.business_entity_guid,
#                 enterprise_guid=enterprise.enterprise_guid,
#                 begin_date=begin_date,
#                 end_date=end_date,
#             )
#             for vet_document in vet_documents:
#                 logger.info(f'vsd: {vet_document.uuid}')
#                 if vet_document.vetDStatus != 'WITHDRAWN':
#                     await Validator(vet_document, vetis, db=db).run()
#                     await asyncio.sleep(0.01)
#             await notifier.push(
#                 str(ProgressMsgSchema(message=(enterprises.index(enterprise) + 1) / enterprises_length * 100)))
#             await asyncio.sleep(0.01)
#     else:
#         be_guids_length = len(be_guids)
#         for guid in be_guids:
#             logger.info(f'- {guid}')
#             try:
#                 enterprises = await vetis.cerberus.get_activity_location_list(guid=guid)
#             except XMLParseError:
#                 logger.info(f'Не удалось получить площадки для предприятия {guid}')
#                 continue
#             for enterprise in enterprises.location:
#                 if enterprise.enterprise.address.region.guid != '4f8b1a21-e4bb-422f-9087-d3cbf4bebc14':
#                     continue
#                 save_enterprise(
#                     db=db,
#                     enterprise=EnterpriseSchema(
#                         enterprise_guid=enterprise.enterprise.guid,
#                         business_entity_guid=guid,
#                     )
#                 )
#                 vet_documents = await get_all_vet_document(
#                     vetis=vetis,
#                     be_guid=guid,
#                     enterprise_guid=enterprise.enterprise.guid,
#                     begin_date=begin_date,
#                     end_date=end_date,
#                 )
#                 for vet_document in vet_documents:
#                     logger.info(f'vsd: {vet_document.uuid}')
#                     if vet_document.vetDStatus != 'WITHDRAWN':
#                         await Validator(vet_document, vetis, db=db).run()
#                         await asyncio.sleep(0.01)
#                 await notifier.push(
#                     str(ProgressMsgSchema(message=(be_guids.index(guid) + 1) / be_guids_length * 100)))
#                 await asyncio.sleep(0.01)
#
#     logger.info(f'Проверка завершена')
#     await notifier.push(str(LogMsgSchema(message=f'Проверка завершена')))
