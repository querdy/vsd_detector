from app.api_v1.schema.base import CamelModel


class EnterpriseSchema(CamelModel):
    enterprise_guid: str
    business_entity_guid: str

    class Config:
        orm_mode = True
