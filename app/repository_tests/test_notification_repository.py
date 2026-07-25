from unittest.mock import Mock

import pytest
from sqlalchemy.exc import SQLAlchemyError

from app.exceptions import NotificationRepositoryError
from app.repositories.notification_repository import NotificationRepository


def test_save_calls_add_commit_and_refresh():
    db = Mock()
    repository = NotificationRepository(db)
    notification = object()

    result = repository.save(notification)

    db.add.assert_called_once_with(notification)
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(notification)
    assert result is notification


def test_save_rolls_back_on_error():
    db = Mock()
    db.commit.side_effect = SQLAlchemyError("db failed")
    repository = NotificationRepository(db)

    with pytest.raises(NotificationRepositoryError):
        repository.save(object())

    db.rollback.assert_called_once()


def test_list_by_user_returns_notifications():
    db = Mock()
    notifications = [object(), object()]
    db.scalars.return_value.all.return_value = notifications
    repository = NotificationRepository(db)

    result = repository.list_by_user(7, unread_only=True)

    assert result == notifications
    db.scalars.assert_called_once()


def test_get_for_user_returns_notification():
    db = Mock()
    notification = object()
    db.scalar.return_value = notification
    repository = NotificationRepository(db)

    result = repository.get_for_user(4, 7)

    assert result is notification
    db.scalar.assert_called_once()


def test_mark_read_updates_and_commits():
    db = Mock()
    notification = Mock(is_read=False)
    repository = NotificationRepository(db)

    result = repository.mark_read(notification)

    assert notification.is_read is True
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(notification)
    assert result is notification
