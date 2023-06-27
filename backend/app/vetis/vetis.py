from app.vetis import clients


class Vetis:
    def __init__(self):
        self.purpose = None
        self.unit = None
        self.dictionary_service = None
        self.cerberus = None
        self.icar = None
        self.mercury = None

    async def create(self,
                     enterprise_login: str,
                     enterprise_password: str,
                     service_id: str = None,
                     issuer_id: str = None,
                     api_key: str = None,
                     initiator: str = None,
                     wsdl_mercury: str = None,
                     wsdl_cerberus: str = None,
                     wsdl_icar: str = None,
                     wsdl_dictionary_service: str = None
                     ):
        if wsdl_mercury is not None:
            self.mercury = clients.Mercury(wsdl_mercury, enterprise_login, enterprise_password,
                                   api_key, service_id, issuer_id, initiator)
        if wsdl_icar is not None:
            self.icar = clients.Icar(wsdl_icar, enterprise_login, enterprise_password)

        if wsdl_cerberus is not None:
            self.cerberus = clients.Cerberus(wsdl_cerberus, enterprise_login, enterprise_password)

        if wsdl_dictionary_service is not None:
            self.dictionary_service = clients.DictionaryService(wsdl_dictionary_service, enterprise_login, enterprise_password)

            self.unit = await self.dictionary_service.get_unit_list()
            self.purpose = await self.dictionary_service.get_purpose_list()
        return self
