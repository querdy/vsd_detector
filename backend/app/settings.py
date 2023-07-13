import re
import secrets
from pathlib import Path

from pydantic import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    BASE_DIR = BASE_DIR
    REPORT_URL: str = "/reports"
    REPORT_ROOT: str = "reports"
    REPORT_DIR: Path = BASE_DIR / "reports"
    API_V1_STR: str = "/api/v1"
    DB_STRING: str = "postgresql+asyncpg://postgres:10120000@localhost/vsd_detector"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    # 60 seconds * 60 minutes * 24 hours = 1 days
    ACCESS_TOKEN_EXPIRE_SECONDS: int = 60 * 60 * 24
    GUID_PATTERN = re.compile('[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}')
    MAIN_REGION_GUID = '4f8b1a21-e4bb-422f-9087-d3cbf4bebc14'

    WSDL_MERCURY: str = 'http://api.vetrf.ru/schema/platform/services/2.0-last/ams-mercury-vu.service_v2.0_production.wsdl'
    WSDL_ICAR: str = 'http://api.vetrf.ru/schema/platform/services/2.1-RC-last/IkarService_v2.1_production.wsdl'
    WSDL_CERBERUS: str = 'http://api.vetrf.ru/schema/platform/services/2.1-RC-last/EnterpriseService_v2.1_production.wsdl'
    WSDL_DICTIONARY_SERVICE = 'http://api.vetrf.ru/schema/platform/services/2.1-RC-last/DictionaryService_v2.1_production.wsdl'


settings = Settings()
