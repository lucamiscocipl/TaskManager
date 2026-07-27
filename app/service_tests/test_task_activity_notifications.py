from types import SimpleNamespace
from unittest.mock import Mock

from app.schemas.task_comments import TaskCommentCreate
from app.services.task_comments_service import TaskCommentService
from app.services.task_image_service import TaskImageService


def test_member_comment_notifies_project_owner_and_assignee():
    author = SimpleNamespace(id=10, username="member")
    project = SimpleNamespace(id=33, owner_id=9)
    task = SimpleNamespace(id=11, user_id=12, title="Fix login")
    saved_comment = SimpleNamespace(id=4)
    service = TaskCommentService(Mock(), author)
    service.require_task_access = Mock(return_value=(project, task))
    service.comments.save = Mock(return_value=saved_comment)
    service.notifications.create_for_users = Mock()

    result = service.submit_comment(
        33,
        11,
        TaskCommentCreate(content="I found the issue"),
    )

    assert result is saved_comment
    service.notifications.create_for_users.assert_called_once_with(
        user_ids={9, 12},
        event_type="task_comment",
        title="New task comment",
        message='member commented on "Fix login"',
        resource_url="/projects/33/tasks/11",
    )


def test_member_image_notifies_project_owner_and_assignee():
    uploader = SimpleNamespace(id=10, username="member")
    project = SimpleNamespace(id=33, owner_id=9)
    task = SimpleNamespace(id=11, user_id=12, title="Fix login")
    saved_image = SimpleNamespace(id=5, original_filename="error.png")
    service = TaskImageService(Mock(), uploader)
    service.require_task_access = Mock(return_value=(project, task))
    service.images.save = Mock(return_value=saved_image)
    service.notifications.create_for_users = Mock()

    result = service.upload_image(
        project_id=33,
        task_id=11,
        filename="error.png",
        content_type="image/png",
        image_data=b"image-data",
    )

    assert result is saved_image
    service.notifications.create_for_users.assert_called_once_with(
        user_ids={9, 12},
        event_type="task_image",
        title="New task image",
        message='member uploaded "error.png" to "Fix login"',
        resource_url="/projects/33/tasks/11",
    )


def test_activity_does_not_notify_the_actor_twice():
    owner = SimpleNamespace(id=9, username="owner")
    project = SimpleNamespace(id=33, owner_id=9)
    task = SimpleNamespace(id=11, user_id=9, title="Fix login")
    saved_image = SimpleNamespace(id=5, original_filename="error.png")
    service = TaskImageService(Mock(), owner)
    service.require_task_access = Mock(return_value=(project, task))
    service.images.save = Mock(return_value=saved_image)
    service.notifications.create_for_users = Mock()

    service.upload_image(
        project_id=33,
        task_id=11,
        filename="error.png",
        content_type="image/png",
        image_data=b"image-data",
    )

    service.notifications.create_for_users.assert_not_called()
