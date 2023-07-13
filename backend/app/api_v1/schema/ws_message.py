import json

from app.api_v1.schema.base import CamelModel


class BaseWSMsgSchema(CamelModel):
    channel: str
    message: str
    status: str | None

    def __str__(self):
        return json.dumps(self.dict())


class LogMsgSchema(BaseWSMsgSchema):
    channel: str = 'log'


class ErrorMsgSchema(BaseWSMsgSchema):
    channel: str = 'error'


class SuccessMsgSchema(BaseWSMsgSchema):
    channel: str = 'success'


class ProgressMsgSchema(BaseWSMsgSchema):
    channel: str = 'progress'


class VSDProgressMsgSchema(BaseWSMsgSchema):
    channel: str = 'vsd_progress'


class FileMsgSchema(BaseWSMsgSchema):
    channel: str = 'file'


class CompleteMsgSchema(BaseWSMsgSchema):
    channel: str = 'complete'


class PredictionMsgSchema(BaseWSMsgSchema):
    channel: str = 'prediction'
