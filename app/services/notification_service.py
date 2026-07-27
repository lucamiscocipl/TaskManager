import logging

from redis.exceptions import RedisError
from sqlalchemy.orm import Session

from app.exceptions import NotificationNotFoundError
from app.models.notifications import Notification
from app.realtime.redis_notifications import publish_notification
from app.repositories.notification_repository import NotificationRepository
from app.schemas.notifications import NotificationResponse

logger = logging.getLogger(__name__)


class NotificationService:
    def __init__(self, db: Session):
        self.notifications = NotificationRepository(db)

    def create_for_users(
        self,
        *,
        user_ids: set[int],
        event_type: str,
        title: str,
        message: str,
        resource_url: str | None = None,
    ) -> list[Notification]:
        created_notifications = []

        for user_id in sorted(user_ids):
            notification = self.notifications.save(
                Notification(
                    user_id=user_id,
                    event_type=event_type,
                    title=title,
                    message=message,
                    resource_url=resource_url,
                )
            )
            created_notifications.append(notification)

            payload = NotificationResponse.model_validate(notification).model_dump(
                mode="json"
            )
            try:
                publish_notification(user_id, payload)
            except RedisError:
                logger.exception(
                    "Could not publish notification %s to Redis",
                    notification.id,
                )

        return created_notifications

    def list_for_user(
        self,
        user_id: int,
        *,
        unread_only: bool = False,
    ) -> list[Notification]:
        return self.notifications.list_by_user(
            user_id,
            unread_only=unread_only,
        )

    def mark_read(
        self,
        notification_id: int,
        user_id: int,
    ) -> Notification:
        notification = self.notifications.get_for_user(notification_id, user_id)
        if notification is None:
            raise NotificationNotFoundError()

        return self.notifications.mark_read(notification)

    def count_unread(self, user_id: int) -> int:
        return self.notifications.count_unread(user_id)

    def mark_all_read(self, user_id: int) -> int:
        return self.notifications.mark_all_read(user_id)
