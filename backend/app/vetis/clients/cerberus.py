from httpx import ReadTimeout
from loguru import logger

from app.vetis.base import Base


class Cerberus(Base):
    def __init__(self,
                 wsdl: str,
                 enterprise_login: str,
                 enterprise_password: str,
                 ):
        self.client_cerberus = self._create_client(wsdl, enterprise_login, enterprise_password)
        self.factory_cerberus = self._create_factory(self.client_cerberus)

    async def get_business_entity_guid_by_inn(self, inn: str):
        response = await self.client_cerberus.service.GetBusinessEntityList(
            businessEntity=self.factory_cerberus.ns3.BusinessEntity(
                inn=inn
            )
        )
        # print(response)
        try:
            return response.businessEntity[0].guid
        except IndexError:
            return False

    async def get_enterprise_by_guid(self, guid: str):
        try:
            response = await self.client_cerberus.service.GetEnterpriseByGuid(
                guid=guid
            )
            return response
        except ReadTimeout:
            logger.info(f'ReadTimeout')

    async def get_business_entity_by_guid(self, guid: str):
        respone = await self.client_cerberus.service.GetBusinessEntityByGuid(
            guid=guid
        )
        return respone

    async def get_activity_location_list(self, guid: str):
        try:
            response = await self.client_cerberus.service.GetActivityLocationList(
                businessEntity=self.factory_cerberus.ns3.BusinessEntity(
                    guid=guid
                )
            )
            return response
        except ReadTimeout:
            logger.info(f'ReadTimeout')

    async def get_russian_enterprise_list(self):
        response = await self.client_cerberus.service.GetRussianEnterpriseList(
            listOptions=self.factory_cerberus.ns1.ListOptions(
                count=500,
                offset=0,
            ),
            enterprise=self.factory_cerberus.ns3.Enterprise(
                guid='d7d0a0bf-9ca1-4f96-bf88-4017ae7928a5'
            )
            # enterprise=self.factory_cerberus.ns3.Enterprise(
            #     address=self.factory_cerberus.ns3.Address(
            #         region=self.factory_cerberus.ns3.Region(
            #             guid='4f8b1a21-e4bb-422f-9087-d3cbf4bebc14',
            #         ),
            #         district=self.factory_cerberus.ns3.District(
            #             guid='7dd380b3-ce33-4280-934f-a4265a07803b'
            #         ),
            #     )
            # )
        )
        print(response)
