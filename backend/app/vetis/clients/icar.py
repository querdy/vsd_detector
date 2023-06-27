from app.vetis.base import Base


class Icar(Base):
    def __init__(self,
                 wsdl: str,
                 enterprise_login: str,
                 enterprise_password: str,
                 ):
        self.client_icar = self._create_client(wsdl, enterprise_login, enterprise_password)
        self.factory_icar = self._create_factory(self.client_icar)

    async def get_all_country_list(self):
        response = await self.client_icar.service.GetAllCountryList(
            listOptions=self.factory_icar.ns1.ListOptions(
                count=500,
            )
        )
        print(response)

    async def get_region_list_by_country_guid(self, country_guid: str = '74a3cbb1-56fa-94f3-ab3f-e8db4940d96b'):
        response = await self.client_icar.service.GetRegionListByCountry(
            listOptions=self.factory_icar.ns1.ListOptions(
                count=500,
            ),
            countryGuid=country_guid,
        )
        print(response)

    async def get_district_list_by_region_guid(self, region_guid: str = '4f8b1a21-e4bb-422f-9087-d3cbf4bebc14'):
        response = await self.client_icar.service.GetDistrictListByRegion(
            listOptions=self.factory_icar.ns1.ListOptions(
                count=500,
            ),
            regionGuid=region_guid,
        )
        print(response)
