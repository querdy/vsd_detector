import asyncio
import datetime

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.api_v1.crud.enterprise import get_enterprises, save_enterprise
from app.api_v1.crud.vet_document import get_vet_documents_by_uuid_list
from app.api_v1.schema.enterprise import EnterpriseSchema
from app.api_v1.schema.ws_message import LogMsgSchema, ProgressMsgSchema, CompleteMsgSchema, FileMsgSchema, \
    VSDProgressMsgSchema, PredictionMsgSchema
from app.api_v1.websocket import notifier
from app.services.excel import get_guids_from_excel
from app.services.vetis import Validator
from app.settings import settings
from app.vetis import Vetis
from app.vetis.clients.mercury import VetisBadServerError, VetisRejectedError
from app.vetis.exceptions import VetisNotResultError


# async def get_vet_documents2(
#         vetis: Vetis,
#         be_guid: str,
#         enterprise_guid: str,
#         begin_date: str,
#         end_date: str):
#     total_vsd = 0
#     offset = 0
#     limit = 300
#     while True:
#         if offset > total_vsd:
#             return
#         await vetis.mercury.get_vet_document_changes_list(
#             owner_guid=be_guid,
#             enterprise_guid=enterprise_guid,
#             begin_date=datetime.datetime.strptime(begin_date, '%Y-%m-%d'),
#             end_date=datetime.datetime.strptime(end_date, '%Y-%m-%d'),
#             count=limit,
#             offset=offset,
#         )
#         try:
#             response = await vetis.mercury.get_finished_response()
#             total_vsd = response.result._value_1.vetDocumentList.total
#             offset += limit
#             vet_documents = response.result._value_1.vetDocumentList.vetDocument
#             if total_vsd > 0:
#                 await notifier.push(
#                     str(VSDProgressMsgSchema(
#                         message=(response.result._value_1.vetDocumentList.count + response.result._value_1.vetDocumentList.offset) / total_vsd * 100)))
#             yield vet_documents
#         except (VetisBadServerError, VetisRejectedError):
#             offset += limit
#             yield []


async def get_vet_documents(
        vetis: Vetis,
        be_guid: str,
        enterprise_guid: str,
        begin_date: str,
        end_date: str):
    total_vsd = 0
    limit = 300
    await vetis.mercury.get_vet_document_changes_list(
        owner_guid=be_guid,
        enterprise_guid=enterprise_guid,
        begin_date=datetime.datetime.strptime(begin_date, '%Y-%m-%d'),
        end_date=datetime.datetime.strptime(end_date, '%Y-%m-%d'),
        count=limit,
    )
    try:
        response = await vetis.mercury.get_finished_response()
        total_vsd = response.result._value_1.vetDocumentList.total
        if total_vsd > 0:
            await notifier.push(
                str(VSDProgressMsgSchema(
                    message=(response.result._value_1.vetDocumentList.count + response.result._value_1.vetDocumentList.offset) / total_vsd * 100
                ))
            )
        yield response.result._value_1.vetDocumentList.vetDocument
    except (VetisBadServerError, VetisRejectedError):
        yield []
    request_queue = []
    logger.info(f'Total vsd: {total_vsd}')
    for index in range(1, total_vsd // limit + 1):
        logger.info(f'{index * limit}/{total_vsd}')
        request = await vetis.mercury.get_vet_document_changes_list(
            owner_guid=be_guid,
            enterprise_guid=enterprise_guid,
            begin_date=datetime.datetime.strptime(begin_date, '%Y-%m-%d'),
            end_date=datetime.datetime.strptime(end_date, '%Y-%m-%d'),
            count=limit,
            offset=index * limit,
        )
        request_queue.append(request)
        await asyncio.sleep(0.01)
    finished_request = []
    while True:
        for request in request_queue:
            response = await vetis.mercury.get_response(application_id=request)
            if response is None:
                continue
            if response.status == 'IN_PROCESS':
                logger.info(f'in_process')
                continue
            if response.status == 'COMPLETED':
                finished_request.append(request)
                await notifier.push(
                    str(VSDProgressMsgSchema(
                        message=(response.result._value_1.vetDocumentList.count + response.result._value_1.vetDocumentList.offset) / total_vsd * 100
                    ))
                )
                logger.info(f'next request')
                yield response.result._value_1.vetDocumentList.vetDocument
            elif response.status == 'REJECTED':
                logger.error(f'заявка отклонена appl.id - {request} - {response.errors.error[0]._value_1}')
                finished_request.append(request)
        await asyncio.sleep(1)
        request_queue = [i for i in request_queue if i not in finished_request]
        if len(request_queue) == 0:
            break


async def backgraund_vsd_examination(
        vetis: Vetis,
        begin_date: str,
        end_date: str,
        db: AsyncSession,
        files: list[bytes] | None):
    start_time = datetime.datetime.now()
    if not files:
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
            async for vet_documents in vet_documents_generator:
                documents_uuid = [vet_document.uuid for vet_document in vet_documents]
                if documents_uuid:
                    checked_vet_documents = await get_vet_documents_by_uuid_list(
                        db=db, documents=documents_uuid
                    )
                    if len(documents_uuid) == len(checked_vet_documents):
                        logger.info(f'Все полученные ВСД уже проверены')
                        continue
                    for vet_document in vet_documents:
                        logger.info(f'vsd: {vet_document.uuid}')
                        if vet_document.uuid in checked_vet_documents:
                            logger.info(f'ВСД уже проверен')
                            continue
                        if vet_document.vetDStatus != 'WITHDRAWN':
                            await Validator(vet_document, vetis, db=db).run()
                await notifier.push(
                    str(ProgressMsgSchema(message=(enterprises.index(enterprise) + 1) / enterprises_length * 100)))
                time_spent = datetime.datetime.now() - start_time
                await notifier.push(
                    str(PredictionMsgSchema(
                        message=str(
                            time_spent / ((enterprises.index(enterprise) + 1) / enterprises_length) - time_spent
                        )
                    ))
                )
                await asyncio.sleep(0.01)

    else:
        for file in files:
            be_guids = get_guids_from_excel(file=file)
            logger.info(f'Обнаружено {len(be_guids)} guid`ов')
            await notifier.push(str(LogMsgSchema(message=f'Обнаружено {len(be_guids)} guid`ов')))
            be_guids_length = len(be_guids)
            for guid in be_guids:
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
                    if enterprise.enterprise.address.region.guid != settings.MAIN_REGION_GUID:
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
                    async for vet_documents in vet_documents_generator:
                        documents_uuid = [vet_document.uuid for vet_document in vet_documents]
                        if documents_uuid:
                            checked_vet_documents = await get_vet_documents_by_uuid_list(
                                db=db, documents=[vet_document.uuid for vet_document in vet_documents]
                            )
                            if len(documents_uuid) == len(checked_vet_documents):
                                logger.info(f'Все полученные ВСД уже проверены')
                                continue
                            for vet_document in vet_documents:
                                await notifier.push(str(FileMsgSchema(message=f"{files.index(file) + 1}/{len(files)}")))
                                logger.info(f'vsd: {vet_document.uuid}')
                                if vet_document.uuid in checked_vet_documents:
                                    logger.info(f'ВСД уже проверен')
                                    continue
                                if vet_document.vetDStatus != 'WITHDRAWN':
                                    await Validator(vet_document, vetis, db=db).run()
                        await notifier.push(
                            str(ProgressMsgSchema(
                                message=(be_guids.index(guid) + 1) / be_guids_length * 100)))
                        await asyncio.sleep(0.01)

    logger.info(f'Проверка завершена')
    await notifier.push(str(LogMsgSchema(message=f'Проверка завершена')))
    await notifier.push(str(CompleteMsgSchema(message=f'Проверка завершен')))
