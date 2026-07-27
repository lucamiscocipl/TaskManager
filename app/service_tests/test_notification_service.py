from unittest.mock import Mock

from app.services.notification_service import NotificationService


def test_list_for_user_passes_unread_filter_by_keyword():
    notifications = [object()]
    service = NotificationService(Mock())
    service.notifications.list_by_user = Mock(return_value=notifications)

    result = service.list_for_user(7, unread_only=True)

    assert result == notifications
    service.notifications.list_by_user.assert_called_once_with(
        7,
        unread_only=True,
    )
