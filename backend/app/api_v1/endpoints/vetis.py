from pathlib import Path

from fastapi import APIRouter, Depends, UploadFile, File, Form
from fastapi.encoders import jsonable_encoder
from fastapi_jwt_auth import AuthJWT
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.responses import JSONResponse, FileResponse

from app import background_tasks
from app.api_v1.crud.report import get_all_reports, get_report_by_uuid
from app.api_v1.crud.user import get_vetis_auth_data_by_user_login
from app.api_v1.schema.base import DateIntervalSchema
from app.api_v1.schema.ws_message import LogMsgSchema
from app.api_v1.websocket import notifier
from app.background_tasks.enterprise_finder import backgraund_enterprise_finder
from app.background_tasks.vsd_examination import backgraund_vsd_examination
from app.settings import settings
from app.database.db import get_db
from app.services.excel import get_guids, create_report
from app.vetis import Vetis

router = APIRouter(prefix="/vetis")


@router.get("/cancel_tasks")
async def cancel_tasks(authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    background_tasks.cancel_tasks()
    return JSONResponse(status_code=status.HTTP_200_OK, content={})


@router.get("/is_running")
async def is_running():
    tasks = background_tasks.get_tasks()
    if tasks:
        return JSONResponse(status_code=status.HTTP_200_OK, content={"detail": True})
    return JSONResponse(status_code=status.HTTP_200_OK, content={"detail": False})


@router.get("/report")
async def get_report(authorize: AuthJWT = Depends(), db: AsyncSession = Depends(get_db)):
    # authorize.jwt_required()
    await background_tasks.add_bg_task(
        create_report,
        db=db
    )
    return JSONResponse(status_code=status.HTTP_200_OK, content={"detail": "Создание отчета запущено"})
    # return FileResponse('report.xlsx', filename="report.xlsx", media_type="application/octet-stream")


@router.get("/reports")
async def get_reports_path(db: AsyncSession = Depends(get_db)):
    reports = await get_all_reports(db=db)
    return JSONResponse(status_code=status.HTTP_200_OK, content={"detail": jsonable_encoder(reports)})


@router.get("/report/{file_uuid}")
async def get_report_file(file_uuid: int, db: AsyncSession = Depends(get_db)):
    file = await get_report_by_uuid(db=db, uuid=file_uuid)
    return FileResponse(
        settings.BASE_DIR / settings.REPORT_ROOT / f"{file.filename}",
        filename=file.filename,
        media_type="application/octet-stream"
    )


@router.post('/run_enterprise_finder')
async def run_enterprise_finder(file: UploadFile = File(),
                                authorize: AuthJWT = Depends(),
                                db: AsyncSession = Depends(get_db)
                                ):
    authorize.jwt_required()
    current_user = authorize.get_jwt_subject()
    auth_data = await get_vetis_auth_data_by_user_login(login=current_user, db=db)
    # guids = await get_guids(file)
    # df = pandas.read_excel(file, sheet_name=1, engine='openpyxl')
    # guids = df['Идентификатор в системе (guid)'].to_list()

    if background_tasks.get_tasks():
        return JSONResponse(status_code=status.HTTP_423_LOCKED, content={
            "detail": "Нельзя запустить две операции одновременно"
        })
    vetis = await Vetis().create(wsdl_mercury=settings.WSDL_MERCURY,
                                 wsdl_cerberus=settings.WSDL_CERBERUS,
                                 wsdl_icar=settings.WSDL_ICAR,
                                 wsdl_dictionary_service=settings.WSDL_DICTIONARY_SERVICE,
                                 service_id=auth_data.service_id,
                                 issuer_id=auth_data.issuer_id,
                                 api_key=auth_data.api_key,
                                 enterprise_login=auth_data.enterprise_login,
                                 enterprise_password=auth_data.enterprise_password,
                                 initiator=auth_data.initiator
                                 )
    logger.info(f'Vetis is created')
    await notifier.push(str(LogMsgSchema(message=f'Vetis is created')))
    if file.filename.endswith('.xlsx'):
        guids = await get_guids(file=file, max_lenght=1000000)
        logger.info(f'Обнаружено {len(guids)} guid`s')
        await notifier.push(str(LogMsgSchema(message=f'Обнаружено {len(guids)} guid`s')))
    else:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": "файл имеет расшираение не .xlsx"}
        )
    await background_tasks.add_bg_task(
        backgraund_enterprise_finder,
        vetis=vetis,
        guids=guids,
        db=db,
    )
    return JSONResponse(status_code=status.HTTP_200_OK, content={"detail": "Сбор площадок успешно запущен"})


@router.post('/run_document_examinator_with_xlsx')
async def run_document_checker(date_interval: DateIntervalSchema = Form(),
                               file: UploadFile = File(),
                               authorize: AuthJWT = Depends(),
                               db: AsyncSession = Depends(get_db)
                               ):
    authorize.jwt_required()
    current_user = authorize.get_jwt_subject()
    auth_data = await get_vetis_auth_data_by_user_login(login=current_user, db=db)
    if background_tasks.get_tasks():
        return JSONResponse(status_code=status.HTTP_423_LOCKED, content={
            "detail": "Нельзя запустить две операции одновременно"
        })

    vetis = await Vetis().create(wsdl_mercury=settings.WSDL_MERCURY,
                                 wsdl_cerberus=settings.WSDL_CERBERUS,
                                 wsdl_icar=settings.WSDL_ICAR,
                                 wsdl_dictionary_service=settings.WSDL_DICTIONARY_SERVICE,
                                 service_id=auth_data.service_id,
                                 issuer_id=auth_data.issuer_id,
                                 api_key=auth_data.api_key,
                                 enterprise_login=auth_data.enterprise_login,
                                 enterprise_password=auth_data.enterprise_password,
                                 initiator=auth_data.initiator
                                 )
    logger.info(f'Vetis is created')
    await notifier.push(str(LogMsgSchema(message=f'Vetis is created')))
    if file.filename.endswith('.xlsx'):
        guids = await get_guids(file=file)
        logger.info(f'Обнаружено {len(guids)} guid`s')
        await notifier.push(str(LogMsgSchema(message=f'Обнаружено {len(guids)} guid`s')))
    else:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": "файл имеет расшираение не .xlsx"}
        )
    await background_tasks.add_bg_task(
        backgraund_vsd_examination,
        vetis=vetis,
        be_guids=guids,
        begin_date=date_interval.date_from,
        end_date=date_interval.date_to,
        db=db,
    )
    return JSONResponse(status_code=status.HTTP_200_OK, content={"detail": "Проверка документов успешно запущена"})


@router.post('/run_document_examinator_without_xlsx')
async def run_document_checker(date_interval: DateIntervalSchema = Form(),
                               authorize: AuthJWT = Depends(),
                               db: AsyncSession = Depends(get_db)
                               ):
    authorize.jwt_required()
    current_user = authorize.get_jwt_subject()
    auth_data = await get_vetis_auth_data_by_user_login(login=current_user, db=db)
    if background_tasks.get_tasks():
        return JSONResponse(status_code=status.HTTP_423_LOCKED, content={
            "detail": "Нельзя запустить две операции одновременно"
        })

    vetis = await Vetis().create(wsdl_mercury=settings.WSDL_MERCURY,
                                 wsdl_cerberus=settings.WSDL_CERBERUS,
                                 wsdl_icar=settings.WSDL_ICAR,
                                 wsdl_dictionary_service=settings.WSDL_DICTIONARY_SERVICE,
                                 service_id=auth_data.service_id,
                                 issuer_id=auth_data.issuer_id,
                                 api_key=auth_data.api_key,
                                 enterprise_login=auth_data.enterprise_login,
                                 enterprise_password=auth_data.enterprise_password,
                                 initiator=auth_data.initiator
                                 )
    logger.info(f'Vetis is created')
    await notifier.push(str(LogMsgSchema(message=f'Vetis is created')))
    await background_tasks.add_bg_task(
        backgraund_vsd_examination,
        vetis=vetis,
        begin_date=date_interval.date_from,
        end_date=date_interval.date_to,
        db=db,
    )
    return JSONResponse(status_code=status.HTTP_200_OK, content={"detail": "Проверка документов успешно запущена"})
