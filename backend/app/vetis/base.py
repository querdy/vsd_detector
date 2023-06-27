from functools import lru_cache

import httpx as httpx
import urllib3
import zeep
from httpx import Timeout
from zeep import AsyncClient, Client, CachingClient
from zeep.transports import AsyncTransport, Transport
from zeep.cache import InMemoryCache

from app.vetis.shared.http_functions import http_login
from app.vetis.shared.type_factory import VetisFactory
from app.vetis.zeep_plugins.plugins import PatchXml
from app.vetis.edit_librarys import edit_zeep

# zeep.loader.load_external = lru_cache()(zeep.loader.load_external)
# zeep.loader.load_external_async = lru_cache()(zeep.loader.load_external_async)


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
    def _create_client(wsdl: str, enterprise_login: str, enterprise_password: str) -> AsyncClient:
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
            operation_timeout=Timeout(10.0),
            cache=InMemoryCache()
        )
        return AsyncClient(
            wsdl,
            transport=transport,
            plugins=[PatchXml()]
        )

    @staticmethod
    def _create_sync_client(wsdl: str, enterprise_login: str, enterprise_password: str) -> Client:
        return CachingClient(
            wsdl=wsdl,
            transport=Transport(
                session=http_login(
                    enterprise_login=enterprise_login,
                    enterprise_password=enterprise_password
                )
            ),
            plugins=[PatchXml()]
        )

    @staticmethod
    def _create_factory(client: zeep.client.Client) -> VetisFactory:
        return VetisFactory(client)
