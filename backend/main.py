import sys

# import uvicorn
# sys.path.append("/home/boyara/bsd_detector/vsd/")
# sys.path.append("/home/boyara/www/vsd/")
from fastapi import FastAPI
from loguru import logger
from starlette.middleware.cors import CORSMiddleware
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.websockets import WebSocketDisconnect, WebSocket

from app.api_v1.router import api_router
from app.api_v1.websocket import notifier
from app.settings import settings
from app.jwt_config import JWTSettings

logger.remove()
logger.add(sys.stderr, level="INFO")
logger.add("file_{time}.log", level="INFO")

app = FastAPI(
    title="Mercury_",
    version="0.1 beta",
    docs_url=f"{settings.API_V1_STR}/docs",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)


# @app.get('/')
# async def dsd():
#     return {'detail': 'hello world'}

@AuthJWT.load_config
def get_config():
    return JWTSettings()


@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(request: Request, exc: AuthJWTException):
    return JSONResponse(status_code=401, content={"detail": exc.message})


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await notifier.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Message text was: {data}")
    except WebSocketDisconnect:
        notifier.remove(websocket)


@app.on_event("startup")
async def startup():
    await notifier.generator.asend(None)

# if __name__ == '__main__':
#     uvicorn.run(app, host="127.0.0.1", port=5050)
#     uvicorn.run(app)
