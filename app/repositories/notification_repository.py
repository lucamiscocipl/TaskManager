from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from app.exceptions import NotificationRepositoryError
from app.models.notifications import Notification
from app.repositories.base_repository import BaseRepository


class NotificationRepository(BaseRepository):
    def save(self, notification: Notification) -> Notification:
        try:
            self.db.add(notification)
            self.db.commit()
            self.db.refresh(notification)
            return notification
        except SQLAlchemyError as error:
            self.db.rollback()
            raise NotificationRepositoryError("save") from error

    def list_by_user(
        self,
        user_id: int,
        *,
        unread_only: bool = False,
        limit: int = 100,
    ) -> list[Notification]:
        try:
            statement = (
                select(Notification)
                .where(Notification.user_id == user_id)
                .order_by(Notification.created_at.desc(), Notification.id.desc())
                .limit(limit)
            )
            if unread_only:
                statement = statement.where(Notification.is_read.is_(False))

            return list(self.db.scalars(statement).all())
        except SQLAlchemyError as error:
            self.db.rollback()
            raise NotificationRepositoryError("list") from error

    def get_for_user(
        self,
        notification_id: int,
        user_id: int,
    ) -> Notification | None:
        try:
            statement = select(Notification).where(
                Notification.id == notification_id,
                Notification.user_id == user_id,
            )
            return self.db.scalar(statement)
        except SQLAlchemyError as error:
            self.db.rollback()
            raise NotificationRepositoryError("read") from error

    def mark_read(self, notification: Notification) -> Notification:
        try:
            notification.is_read = True
            self.db.commit()
            self.db.refresh(notification)
            return notification
        except SQLAlchemyError as error:
            self.db.rollback()
            raise NotificationRepositoryError("update") from error
