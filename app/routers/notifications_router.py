import asyncio
from typing import Annotated

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, status
from sqlalchemy.orm import Session

from app.database import get_db, session_local
from app.dependencies import get_current_user, get_user_from_token
from app.exceptions import TokenValidationError
from app.models.user import User
from app.realtime.connection_manager import notification_connections
from app.schemas.notifications import (
    NotificationResponse,
    NotificationsMarkedReadResponse,
    NotificationUnreadCountResponse,
)
from app.services.notification_service import NotificationService

router = APIRouter(tags=["Notifications"])
AUTHENTICATION_TIMEOUT_SECONDS = 5


def get_notification_service(
    db: Session = Depends(get_db),
) -> NotificationService:
    return NotificationService(db)


NotificationServiceDep = Annotated[
    NotificationService,
    Depends(get_notification_service),
]


@router.get(
    "/notifications",
    response_model=list[NotificationResponse],
)
def list_notifications(
    service: NotificationServiceDep,
    unread_only: bool = False,
    current_user: User = Depends(get_current_user),
):
    return service.list_for_user(
        current_user.id,
        unread_only=unread_only,
    )


@router.get(
    "/notifications/unread-count",
    response_model=NotificationUnreadCountResponse,
)
def get_unread_notification_count(
    service: NotificationServiceDep,
    current_user: User = Depends(get_current_user),
):
    return NotificationUnreadCountResponse(
        unread_count=service.count_unread(current_user.id)
    )


@router.patch(
    "/notifications/read-all",
    response_model=NotificationsMarkedReadResponse,
)
def mark_all_notifications_read(
    service: NotificationServiceDep,
    current_user: User = Depends(get_current_user),
):
    return NotificationsMarkedReadResponse(
        updated_count=service.mark_all_read(current_user.id)
    )


@router.patch(
    "/notifications/{notification_id}/read",
    response_model=NotificationResponse,
)
def mark_notification_read(
    notification_id: int,
    service: NotificationServiceDep,
    current_user: User = Depends(get_current_user),
):
    return service.mark_read(notification_id, current_user.id)


@router.websocket("/ws/notifications")
async def notification_websocket(websocket: WebSocket) -> None:
    await websocket.accept()

    try:
        authentication = await asyncio.wait_for(
            websocket.receive_json(),
            timeout=AUTHENTICATION_TIMEOUT_SECONDS,
        )
    except TimeoutError:
        await websocket.close(
            code=status.WS_1008_POLICY_VIOLATION,
            reason="Authentication timed out",
        )
        return
    except ValueError, WebSocketDisconnect:
        return

    if authentication.get("type") != "authenticate":
        await websocket.close(
            code=status.WS_1008_POLICY_VIOLATION,
            reason="Authentication is required",
        )
        return

    token = authentication.get("token")
    if not isinstance(token, str):
        await websocket.close(
            code=status.WS_1008_POLICY_VIOLATION,
            reason="A valid access token is required",
        )
        return

    try:
        with session_local() as db:
            user_id = get_user_from_token(token, db).id
    except TokenValidationError:
        await websocket.close(
            code=status.WS_1008_POLICY_VIOLATION,
            reason="Invalid or expired access token",
        )
        return

    notification_connections.register(user_id, websocket)
    await websocket.send_json({"type": "connection.ready"})

    try:
        while True:
            message = await websocket.receive_json()
            if message.get("type") == "ping":
                await websocket.send_json({"type": "pong"})
    except ValueError, WebSocketDisconnect:
        pass
    finally:
        notification_connections.disconnect(user_id, websocket)
