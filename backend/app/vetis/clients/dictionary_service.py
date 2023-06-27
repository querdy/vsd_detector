from app.vetis.base import Base


class DictionaryService(Base):
    def __init__(self,
                 wsdl: str,
                 enterprise_login: str,
                 enterprise_password: str,
                 ):
        self.client_dictionary_service = self._create_client(wsdl, enterprise_login, enterprise_password)
        self.factory_dictionary_service = self._create_factory(self.client_dictionary_service)

    async def get_unit_list(self):
        response = await self.client_dictionary_service.service.GetUnitList()
        unit = {unit['guid']: unit['name'] for unit in response.unit}
        return unit

    async def get_purpose_list(self):
        response = await self.client_dictionary_service.service.GetPurposeList(
            listOptions=self.factory_dictionary_service.ns1.ListOptions(
                count=500,
                offset=0
            )
        )
        purpose = {purpose['guid']: purpose['name'] for purpose in response.purpose}
        return purpose
