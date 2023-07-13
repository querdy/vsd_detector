from starlette.websockets import WebSocket
from websockets.exceptions import ConnectionClosedError


class Notifier:
    def __init__(self):
        self.connections: list[WebSocket] = []
        self.generator = self.get_notification_generator()

    async def get_notification_generator(self):
        while True:
            message = yield
            await self._notify(message)

    async def push(self, msg: str):
        await self.generator.asend(msg)

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.connections.append(websocket)

    def remove(self, websocket: WebSocket):
        try:
            self.connections.remove(websocket)
        except ValueError:
            pass

    async def _notify(self, message: str):
        living_connections = []
        while len(self.connections) > 0:
            try:
                websocket = self.connections.pop()
                await websocket.send_text(message)
                living_connections.append(websocket)
            except ConnectionClosedError:
                pass
        self.connections = living_connections


notifier = Notifier()

