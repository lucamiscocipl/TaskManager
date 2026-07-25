from collections import defaultdict

from fastapi import WebSocket


class NotificationConnectionManager:
    def __init__(self):
        self.connections: dict[int, set[WebSocket]] = defaultdict(set)

    async def connect(self, user_id: int, websocket: WebSocket) -> None:
        await websocket.accept()
        self.register(user_id, websocket)

    def register(self, user_id: int, websocket: WebSocket) -> None:
        self.connections[user_id].add(websocket)

    def disconnect(self, user_id: int, websocket: WebSocket) -> None:
        sockets = self.connections.get(user_id)

        if sockets is None:
            return

        sockets.discard(websocket)

        if not sockets:
            self.connections.pop(user_id, None)

    async def send_to_user(self, user_id: int, payload: dict) -> None:
        failed: list[WebSocket] = []

        for websocket in list(self.connections.get(user_id, set())):
            try:
                await websocket.send_json(payload)
            except Exception:
                failed.append(websocket)

        for websocket in failed:
            self.disconnect(user_id, websocket)


notification_connections = NotificationConnectionManager()
