import httpx as httpx
import urllib3
import zeep
from httpx import Timeout
from zeep import AsyncClient
from zeep.transports import AsyncTransport
from zeep.cache import InMemoryCache

from app.vetis.shared.type_factory import VetisFactory
from app.vetis.zeep_plugins.plugins import PatchXml
from app.vetis.edit_librarys import edit_zeep


class VetDocumentType:
    INCOMING = 'INCOMING'  # входящий
    OUTGOING = 'OUTGOING'  # исходящий
    PRODUCTIVE = 'PRODUCTIVE'  # производственный
    TRANSPORT = 'TRANSPORT'  # транспортный
    RETURNABLE = 'RETURNABLE'  # возвратный


class VetDocumentStatus:
    CONFIRMED = 'CONFIRMED'  # подтверждён
    WITHDRAWN = 'WITHDRAWN'  # аннулирован
    UTILIZED = 'UTILIZED'  # погашен


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class Base:
    @staticmethod
    def _create_client(wsdl: str, enterprise_login: str, enterprise_password: str, settings: zeep.Settings = None) -> AsyncClient:
        async_client = httpx.AsyncClient(
            auth=(enterprise_login, enterprise_password),
            verify=True,
        )
        wsdl_client = httpx.Client(
            auth=(enterprise_login, enterprise_password),
            verify=True,
        )
        transport = AsyncTransport(
            client=async_client,
            wsdl_client=wsdl_client,
            operation_timeout=Timeout(5.0),
            cache=InMemoryCache()
        )
        return AsyncClient(
            wsdl,
            settings=settings,
            transport=transport,
            plugins=[PatchXml()]
        )

    @staticmethod
    def _create_factory(client: zeep.client.Client) -> VetisFactory:
        return VetisFactory(client)
