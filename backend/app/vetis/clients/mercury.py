import asyncio
import datetime

from httpx import ReadTimeout
from loguru import logger
from zeep import xsd

from app.vetis.base import Base


def _push(method):
    def wrapper(self, *args, **kwargs):
        return self._push_request(method(self, *args, **kwargs))

    return wrapper


class VetisRejectedError(Exception):
    ...


class VetisBadServerError(Exception):
    ...


class Mercury(Base):
    def __init__(self,
                 wsdl: str,
                 enterprise_login: str,
                 enterprise_password: str,
                 api_key: str,
                 service_id: str,
                 issuer_id: str,
                 initiator: str,
                 ):
        self.api_key = api_key
        self.service_id = service_id
        self.issuer_id = issuer_id
        self.initiator = initiator
        self.last_application_id = None
        self.client_mercury = self._create_client(wsdl, enterprise_login, enterprise_password)
        self.factory_mercury = self._create_factory(self.client_mercury)

    async def _push_request(self, application):
        request = await self.client_mercury.service.submitApplicationRequest(
            apiKey=self.api_key,
            application=self.factory_mercury.ns2.Application(
                serviceId=self.service_id,
                issuerId=self.issuer_id,
                issueDate=datetime.datetime.now(),
                data=self.factory_mercury.ns2.ApplicationDataWrapper(
                    _value_1=application)
            ))
        logger.debug(request)

        self.last_application_id = request.applicationId
        return request.applicationId

    async def get_response(self, application_id: str = None):
        application_id = application_id or self.last_application_id
        response = await self.client_mercury.service.receiveApplicationResult(
            apiKey=self.api_key,
            issuerId=self.issuer_id,
            applicationId=application_id)
        logger.debug(response)
        return response

    async def get_finished_response(self, application_id: str = None, iterations: int = 30):
        application_id = application_id or self.last_application_id
        for index in range(iterations):
            logger.info(f'Попытка получения ответа {index + 1}')
            await asyncio.sleep(1)
            try:
                response = await self.client_mercury.service.receiveApplicationResult(
                    apiKey=self.api_key,
                    issuerId=self.issuer_id,
                    applicationId=application_id)
            except ReadTimeout:
                logger.info(f'ReadTimeout')
            if index == iterations - 1 and response.status == 'IN_PROCESS':
                raise VetisBadServerError('Сервер не в настроении')
            if response.status == 'COMPLETED':
                return response
            elif response.status == 'REJECTED':
                logger.info(f'заявка отклонена appl. id - {application_id} - {response.errors.error[0]._value_1}')
                raise VetisRejectedError('Заявка отклонена')
            # await asyncio.sleep(1)

    @_push
    def get_business_entity_user(self,
                                 login: str,
                                 local_transaction_id="Boyara©"
                                 ):
        _element = self.client_mercury.get_element('ns4:getBusinessEntityUserRequest')
        application = xsd.AnyObject(_element, _element(
            localTransactionId=local_transaction_id,
            initiator=self.factory_mercury.ns6.User(
                login=self.initiator),
            user=self.factory_mercury.ns6.User(
                login=login
            )
        ))
        return application

    @_push
    def get_stock_entry_list(self,
                             owner_guid: str,
                             enterprise_guid: str,
                             local_transaction_id: str = "Boyara©",
                             count: int = 10,
                             offset: int = 0
                             ):
        _element = self.client_mercury.get_element('ns4:getStockEntryListRequest')
        application = xsd.AnyObject(_element, _element(
            localTransactionId=local_transaction_id,
            initiator=self.factory_mercury.ns6.User(
                login=self.initiator),
            listOptions=self.factory_mercury.ns1.ListOptions(count=count, offset=offset),
            businessMember=self.factory_mercury.ns5.BusinessMember(
                businessEntity=self.factory_mercury.ns5.BusinessEntity(
                    guid=owner_guid),
                enterprise=self.factory_mercury.ns5.Enterprise(
                    guid=enterprise_guid)),
        ))
        return application

    @_push
    def get_vet_document_changes_list(self,
                                      owner_guid: str,
                                      enterprise_guid: str,
                                      begin_date: datetime.datetime,
                                      end_date: datetime.datetime,
                                      local_transaction_id: str = "Boyara©",
                                      count: int = 500,
                                      offset: int = 0
                                      ):
        _element = self.client_mercury.get_element('ns4:getVetDocumentChangesListRequest')
        application = xsd.AnyObject(_element, _element(
            localTransactionId=local_transaction_id,
            initiator=self.factory_mercury.ns6.User(
                login=self.initiator),
            listOptions=self.factory_mercury.ns1.ListOptions(
                count=count,
                offset=offset),
            updateDateInterval=self.factory_mercury.ns1.DateInterval(
                beginDate=begin_date,
                endDate=end_date),
            businessMember=self.factory_mercury.ns5.BusinessMember(
                businessEntity=self.factory_mercury.ns5.BusinessEntity(
                    guid=owner_guid),
                enterprise=self.factory_mercury.ns5.Enterprise(
                    guid=enterprise_guid)),
        ))
        return application

    @_push
    def get_vet_document_list(self,
                              owner_guid: str,
                              enterprise_guid: str,
                              vet_document_type: str = None,
                              vet_document_status: str = None,
                              local_transaction_id: str = "Boyara©",
                              count: int = 1000,
                              offset: int = 0
                              ):
        _vet_document_type = self.factory_mercury.ns6.VetDocumentType(
            vet_document_type) if vet_document_type is not None else None
        _vet_document_status = self.factory_mercury.ns6.VetDocumentType(
            vet_document_status) if vet_document_status is not None else None

        _element = self.client_mercury.get_element('ns4:getVetDocumentListRequest')
        application = xsd.AnyObject(_element, _element(
            localTransactionId=local_transaction_id,
            initiator=self.factory_mercury.ns6.User(
                login=self.initiator),
            listOptions=self.factory_mercury.ns1.ListOptions(
                count=count,
                offset=offset),
            vetDocumentType=_vet_document_type,
            vetDocumentStatus=_vet_document_status,
            businessMember=self.factory_mercury.ns5.BusinessMember(
                businessEntity=self.factory_mercury.ns5.BusinessEntity(
                    guid=owner_guid),
                enterprise=self.factory_mercury.ns5.Enterprise(
                    guid=enterprise_guid)),
        ))
        return application

    @_push
    def get_vet_document_by_uuid(self,
                                 uuid: str,
                                 local_transaction_id: str = "Boyara©",
                                 ):
        _element = self.client_mercury.get_element('ns4:getVetDocumentByUuidRequest')
        application = xsd.AnyObject(_element, _element(
            localTransactionId=local_transaction_id,
            initiator=self.factory_mercury.ns6.User(
                login=self.initiator),
            uuid=uuid.lower(),
            enterpriseGuid='97b586a6-8309-4317-a9f0-65ec5e99623c'
        ))
        return application

    @_push
    def process_incoming_consignment_for_document(
            self,
            confirmed_vet_document,
            local_transaction_id: str = "Boyara©"
    ):
        _element = self.client_mercury.get_element('ns4:processIncomingConsignmentRequest')

        waybill = None
        for referenced_document in confirmed_vet_document.referencedDocument:
            if referenced_document.type in (1, 2, 3, 4, 5):
                waybill = referenced_document
        if waybill is not None:
            _waybill = self.factory_mercury.ns6.Waybill(
                issueSeries=waybill.issueSeries,
                issueNumber=waybill.issueNumber,
                issueDate=waybill.issueDate,
                type=waybill.type,
            )
        else:
            _waybill = None

        application = xsd.AnyObject(_element, _element(
            localTransactionId=local_transaction_id,
            initiator=self.factory_mercury.ns6.User(
                login=self.initiator),
            delivery=self.factory_mercury.ns6.Delivery(
                deliveryDate=datetime.datetime.now(),
                consignor=self.factory_mercury.ns5.BusinessMember(
                    businessEntity=self.factory_mercury.ns5.BusinessEntity(
                        guid=confirmed_vet_document.certifiedConsignment.consignor.businessEntity.guid),
                    enterprise=self.factory_mercury.ns5.Enterprise(
                        guid=confirmed_vet_document.certifiedConsignment.consignor.enterprise.guid)),
                consignee=self.factory_mercury.ns5.BusinessMember(
                    businessEntity=self.factory_mercury.ns5.BusinessEntity(
                        guid=confirmed_vet_document.certifiedConsignment.consignee.businessEntity.guid),
                    enterprise=self.factory_mercury.ns5.Enterprise(
                        guid=confirmed_vet_document.certifiedConsignment.consignee.enterprise.guid)
                ),
                consignment=self.factory_mercury.ns6.Consignment(
                    productType=confirmed_vet_document.certifiedConsignment.batch.productType,
                    product=confirmed_vet_document.certifiedConsignment.batch.product,
                    subProduct=confirmed_vet_document.certifiedConsignment.batch.subProduct,
                    productItem=confirmed_vet_document.certifiedConsignment.batch.productItem,
                    volume=confirmed_vet_document.certifiedConsignment.batch.volume,
                    unit=confirmed_vet_document.certifiedConsignment.batch.unit,
                    dateOfProduction=confirmed_vet_document.certifiedConsignment.batch.dateOfProduction,
                    expiryDate=confirmed_vet_document.certifiedConsignment.batch.expiryDate,
                    perishable=confirmed_vet_document.certifiedConsignment.batch.perishable,
                    origin=confirmed_vet_document.certifiedConsignment.batch.origin,
                    packageList=confirmed_vet_document.certifiedConsignment.batch.packageList,
                ),
                broker=confirmed_vet_document.certifiedConsignment.broker,
                transportInfo=confirmed_vet_document.certifiedConsignment.transportInfo,
                transportStorageType=confirmed_vet_document.certifiedConsignment.transportStorageType,
                accompanyingForms=self.factory_mercury.ns6.ConsignmentDocumentList(
                    waybill=_waybill,
                    vetCertificate=self.factory_mercury.ns6.VetDocument(
                        uuid=confirmed_vet_document.uuid
                    )
                ),
            ),
            deliveryFacts=self.factory_mercury.ns6.DeliveryFactList(
                vetCertificatePresence='ELECTRONIC',
                docInspection=self.factory_mercury.ns6.DeliveryInspection(
                    result='CORRESPONDS'
                ),
                vetInspection=self.factory_mercury.ns6.DeliveryInspection(
                    result='UNSUPERVISED'
                ),
                decision='ACCEPT_ALL',
            ),

        )
                                    )
        return application

    @_push
    def process_incoming_consignment(self,
                                     consignor_guid: str,
                                     consignor_enterprise_guid: str,
                                     consignee_guid: str,
                                     consignee_enterprise_guid: str,
                                     product_type: str,
                                     product: str,
                                     product_item: str,
                                     sub_product: str,
                                     volume: float,
                                     unit: str,
                                     date_of_production,
                                     expiry_date,
                                     perishable: bool,
                                     origin,
                                     package_list,
                                     broker,
                                     transport_info,
                                     transport_storage_type,
                                     waybill,
                                     vet_doc_uuid: str,
                                     local_transaction_id: str = "Boyara©"
                                     ):
        _element = self.client_mercury.get_element('ns4:processIncomingConsignmentRequest')
        if waybill is not None:
            _waybill = self.factory_mercury.ns6.Waybill(
                issueSeries=waybill.issueSeries,
                issueNumber=waybill.issueNumber,
                issueDate=waybill.issueDate,
                type=waybill.type,
            )
        else:
            _waybill = None

        application = xsd.AnyObject(_element, _element(
            localTransactionId=local_transaction_id,
            initiator=self.factory_mercury.ns6.User(
                login=self.initiator),
            delivery=self.factory_mercury.ns6.Delivery(
                deliveryDate=datetime.datetime.now(),
                consignor=self.factory_mercury.ns5.BusinessMember(
                    businessEntity=self.factory_mercury.ns5.BusinessEntity(
                        guid=consignor_guid),
                    enterprise=self.factory_mercury.ns5.Enterprise(
                        guid=consignor_enterprise_guid)),
                consignee=self.factory_mercury.ns5.BusinessMember(
                    businessEntity=self.factory_mercury.ns5.BusinessEntity(
                        guid=consignee_guid),
                    enterprise=self.factory_mercury.ns5.Enterprise(
                        guid=consignee_enterprise_guid)
                ),
                consignment=self.factory_mercury.ns6.Consignment(
                    productType=product_type,
                    product=product,
                    subProduct=sub_product,
                    productItem=product_item,
                    volume=volume,
                    unit=unit,
                    dateOfProduction=date_of_production,
                    expiryDate=expiry_date,
                    perishable=perishable,
                    origin=origin,
                    packageList=package_list,
                ),
                broker=broker,
                transportInfo=transport_info,
                transportStorageType=transport_storage_type,
                accompanyingForms=self.factory_mercury.ns6.ConsignmentDocumentList(
                    waybill=_waybill,
                    vetCertificate=self.factory_mercury.ns6.VetDocument(
                        uuid=vet_doc_uuid
                    )
                ),
            ),
            deliveryFacts=self.factory_mercury.ns6.DeliveryFactList(
                vetCertificatePresence='ELECTRONIC',
                docInspection=self.factory_mercury.ns6.DeliveryInspection(
                    result='CORRESPONDS'
                ),
                vetInspection=self.factory_mercury.ns6.DeliveryInspection(
                    result='UNSUPERVISED'
                ),
                decision='ACCEPT_ALL',
            ),

        )
                                    )
        return application
