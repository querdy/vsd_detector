import asyncio
import json
import re
from datetime import datetime

from loguru import logger
from sqlalchemy.orm import Session
from zeep.exceptions import XMLParseError

from app import settings
from app.api_v1.crud.vet_document import get_checked_document_by_vet_document_uuid, save_vet_document
from app.api_v1.schema.vet_document import CheckedDocumentSchema
from app.api_v1.schema.ws_message import LogMsgSchema
from app.api_v1.websocket import notifier
from app.services.cache import Cache
from app.vetis import Vetis

enterprise_cache = Cache(16)
quarantine_cache = Cache(16)

with open(settings.BASE_DIR/'app/static/failed_purpose.json', 'r', encoding='utf-8') as f:
    failed_purpose = json.load(f)

with open(settings.BASE_DIR/'app/static/quarantine_purpose.json', 'r', encoding='utf-8') as f:
    quarantine_purpose = json.load(f)

with open(settings.BASE_DIR/'app/static/lab_name.json', 'r', encoding='utf-8') as f:
    laboratories = set(json.load(f))


def verified_vse(vet_document) -> bool:
    vse_product_type = [1, 2, 5, 7]
    if vet_document.certifiedConsignment.batch.productType in vse_product_type:
        if vet_document.authentication.cargoExpertized == 'UNFULFILLED':
            logger.info(
                f'"Не подвергнуто ВСЭ" - {vet_document.uuid} - {vet_document.statusChange[0].specifiedPerson.fio}')
            raise VSDValidationError(f'Не подвергнуто ВСЭ')
    return True


def verified_packing(vet_document) -> bool:
    package_product_type = [1, 2, 4, 5, 6, 7]
    if vet_document.certifiedConsignment.batch.productType in package_product_type:
        if vet_document.certifiedConsignment.batch.packageList is None:
            logger.info(
                f'Не указана упаковка - {vet_document.uuid} - {vet_document.statusChange[0].specifiedPerson.fio}')
            raise VSDValidationError(f'Не указана упаковка')
    return True


async def verified_consignee_enterprise(vet_document, vetis: Vetis) -> bool:
    consignee_guid = vet_document.certifiedConsignment.consignee.enterprise.guid
    match enterprise_cache.get(consignee_guid):
        case True:
            return True
        case False:
            raise VSDValidationError(f'ВСД оформлен на неподтвержденную площадку')
        case None:
            try:
                responsed_enterprise = await vetis.cerberus.get_enterprise_by_guid(consignee_guid)
                if responsed_enterprise is None:
                    return False
            except XMLParseError:
                logger.info(f'Не удалось получить данные площадки')
                enterprise_cache[consignee_guid] = True
                return False
            if responsed_enterprise.registryStatus != 'VERIFIED':
                enterprise_cache[consignee_guid] = False
                # verified_consignee_enterprise_chache.update({consignee_guid: False})
                logger.info(
                    f'ВСД оформлен на неподтвержденную площадку - '
                    f'{vet_document.uuid} - '
                    f'{vet_document.statusChange[0].specifiedPerson.fio}')
                raise VSDValidationError(f'ВСД оформлен на неподтвержденную площадку')
            enterprise_cache[consignee_guid] = True
            return True


def verified_producer_enterprise_count(vet_document) -> bool:
    if len(vet_document.certifiedConsignment.batch.origin.producer) == 1:
        return True
    logger.info(
        f'Более 1 (одного) предприятия-производителя - {vet_document.uuid} - {vet_document.statusChange[0].specifiedPerson.fio}')
    raise VSDValidationError(f'Более 1 (одного) предприятия-производителя')


def verified_animal_spent_period(vet_document) -> bool:
    if not vet_document.authentication.animalSpentPeriod == 'ZERO':
        logger.info(
            f'Животные не находились на территории ТС - {vet_document.uuid} - {vet_document.statusChange[0].specifiedPerson.fio}')
        raise VSDValidationError(f'Животные не находились на территории ТС')
    return True


def verified_transport_storage_type(vet_document) -> bool:
    if vet_document.certifiedConsignment.batch.productType == 3:
        if vet_document.certifiedConsignment.transportStorageType != 'VENTILATED':
            logger.info(
                f'Для живых животных условия перевозки не "вентелируемый" - {vet_document.uuid} - {vet_document.statusChange[0].specifiedPerson.fio}')
            raise VSDValidationError(f'Для живых животных условия перевозки не "вентелируемый"')
    elif ' охл' in vet_document.certifiedConsignment.batch.productItem.name:
        if vet_document.certifiedConsignment.transportStorageType != 'CHILLED':
            logger.info(
                f'Для охлажденной продукции способ перевозки не "охлажденный" - {vet_document.uuid} - {vet_document.statusChange[0].specifiedPerson.fio}')
            raise VSDValidationError(f'Для охлажденной продукции способ перевозки не "охлажденный"')
    elif ' зам' in vet_document.certifiedConsignment.batch.productItem.name or \
            'морож' in vet_document.certifiedConsignment.batch.productItem.name:
        if vet_document.certifiedConsignment.transportStorageType != 'FROZEN':
            logger.info(
                f'Для замороженной продукции способ перевозки не "замороженный" - {vet_document.uuid} - {vet_document.statusChange[0].specifiedPerson.fio}')
            raise VSDValidationError(f'Для замороженной продукции способ перевозки не "замороженный"')
    return True


def verified_expiration_date(vet_document) -> bool:
    try:
        if vet_document.certifiedBatch.batch.dateOfProduction.secondDate is None and \
                vet_document.certifiedBatch.batch.expiryDate.secondDate is None:
            return True
        else:
            logger.info(
                f'Дата выработки/ срок годности указаны интервалом - {vet_document.uuid} - {vet_document.statusChange[0].specifiedPerson.fio}')
            raise VSDValidationError(f'Дата выработки/ срок годности указаны интервалом')
    except AttributeError:
        if vet_document.certifiedBatch.batch.dateOfProduction.secondDate is None:
            return True
        else:
            logger.info(
                f'Дата выработки/ срок годности указаны интервалом - {vet_document.uuid} - {vet_document.statusChange[0].specifiedPerson.fio}')
            raise VSDValidationError(f'Дата выработки/ срок годности указаны интервалом')


async def verified_quarantine(vet_document, vetis: Vetis) -> bool:
    consignor_region_guid = quarantine_cache.get(vet_document.certifiedConsignment.consignor.enterprise.guid)
    consignee_region_guid = quarantine_cache.get(vet_document.certifiedConsignment.consignee.enterprise.guid)
    try:
        if consignor_region_guid is None:
            consignor_region_guid = await vetis.cerberus.get_enterprise_by_guid(
                vet_document.certifiedConsignment.consignor.enterprise.guid)
            quarantine_cache[vet_document.certifiedConsignment.consignor.enterprise.guid] = consignor_region_guid
    except XMLParseError:
        logger.info(
            f'Не удалось получить данные площадки '
            f'{vet_document.certifiedConsignment.consignor.enterprise.guid}'
        )
        return False
    try:
        if consignee_region_guid is None:
            consignee_region_guid = await vetis.cerberus.get_enterprise_by_guid(
                vet_document.certifiedConsignment.consignee.enterprise.guid)
            quarantine_cache[vet_document.certifiedConsignment.consignee.enterprise.guid] = consignee_region_guid
    except XMLParseError:
        logger.info(
            f'Не удалось получить данные площадки {vet_document.certifiedConsignment.consignee.enterprise.guid}')
        return False

    if consignor_region_guid is None or consignee_region_guid is None:
        return False
    if consignor_region_guid == consignee_region_guid:
        return True
    else:
        if vet_document.authentication.purpose.guid in quarantine_purpose.keys():
            if vet_document.authentication.quarantine.duration > 0:
                return True
            else:
                logger.info(
                    f'Отсутствует карантин - {vet_document.uuid} - {vet_document.statusChange[0].specifiedPerson.fio}')
                raise VSDValidationError(f'Отсутствует карантин')


def verified_laboratory(vet_document) -> bool:
    reg = re.compile('[^a-zA-ZА-Яа-я0-9 ]')
    for research in vet_document.authentication.laboratoryResearch:
        try:
            if reg.sub('', research.operator.name) not in laboratories:
                logger.info(
                    f'{research.operator.name} - нет в списке лабораторий - {vet_document.uuid} - {vet_document.statusChange[0].specifiedPerson.fio}')
                # raise VSDValidationError(f'{research.operator.name} - нет в списке лабораторий')
                raise VSDValidationError(f'Некорректно указана лаборатория')
        except AttributeError:
            logger.info(f'Отсутствует название лаборатории??? - {vet_document.uuid}')
        return True


def verified_purpose(vet_document) -> bool:
    if vet_document.authentication.purpose.guid in failed_purpose.keys():
        if vet_document.certifiedConsignment.batch.productType == 2 and vet_document.authentication.purpose.guid == "5b91502d-e089-11e1-bcf3-b499babae7ea":
            return True
        logger.info(
            f'Выбрана цель {purposes[vet_document.authentication.purpose.guid]} - {vet_document.uuid} - {vet_document.statusChange[0].specifiedPerson.fio}')
        raise VSDValidationError(f'Явно ошибочная цель')
    return True


class VSDValidationError(Exception):
    pass


class Validator:
    validators_mapper = {
        "LIC1": [verified_consignee_enterprise, verified_producer_enterprise_count, verified_animal_spent_period,
                 verified_transport_storage_type, verified_quarantine, verified_laboratory, verified_purpose],
        "LIC2": [verified_producer_enterprise_count, verified_vse, verified_packing, verified_consignee_enterprise,
                 verified_laboratory, verified_purpose],
        "LIC3": [verified_producer_enterprise_count, verified_vse, verified_packing, verified_consignee_enterprise,
                 verified_laboratory, verified_purpose],
        "NOTE4_ANIMALS": [verified_animal_spent_period, verified_transport_storage_type,
                          verified_producer_enterprise_count, verified_consignee_enterprise, verified_laboratory,
                          verified_purpose],
        "NOTE4_PRODUCTS": [verified_vse, verified_packing, verified_transport_storage_type,
                           verified_producer_enterprise_count, verified_consignee_enterprise, verified_laboratory,
                           verified_purpose],
        "PRODUCTIVE": [verified_expiration_date]
    }

    def __init__(self, vet_document, vetis: Vetis, db: Session):
        self.vetis = vetis
        self.vet_document = vet_document
        self.validators = None
        self.errors = []
        self.db = db

    async def run(self):
        if get_checked_document_by_vet_document_uuid(
                db=self.db,
                vet_document_uuid=self.vet_document.uuid):
            logger.info(f'ВСД уже проверен')
            return
        self.set_validators()
        if self.validators is not None:
            await self.validate()
            if self.errors:
                await notifier.push(str(LogMsgSchema(
                    message=f'{self.vet_document.uuid} - {self.errors} - {self.vet_document.statusChange[0].specifiedPerson.fio}')))
            self.save()
        else:
            logger.info(f'Сертефикат РСХН (импорт)')

    async def validate(self):
        for validator in self.validators:
            # start = datetime.now()
            try:
                if asyncio.iscoroutinefunction(validator):
                    await validator(self.vet_document, self.vetis)
                else:
                    validator(self.vet_document)
            except VSDValidationError as err:
                self.errors.append(str(err))
            # end = datetime.now() - start
            # print(f'{validator} - {end}')

    def set_validators(self):
        vet_document_form = self.vet_document.vetDForm
        if vet_document_form == 'NOTE4':
            if self.vet_document.certifiedConsignment.batch.productType == 3:
                vet_document_form = 'NOTE4_ANIMALS'
            else:
                vet_document_form = 'NOTE4_PRODUCTS'
        self.validators = self.validators_mapper.get(vet_document_form)

    def save(self):
        save_vet_document(
            db=self.db,
            vet_document=CheckedDocumentSchema(
                vet_document_uuid=self.vet_document.uuid,
                saved_datetime=datetime.utcnow(),
                is_mistakes=bool(len(self.errors)),
                person=self.vet_document.statusChange[0].specifiedPerson.fio,
                description=", ".join(self.errors)
            )
        )
