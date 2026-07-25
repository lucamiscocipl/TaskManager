from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from app.exceptions import (
    ProjectMembershipRequiredError,
    TaskAlreadyAssignedError,
)
from app.schemas.tasks import TaskCreate
from app.services.project_service import ProjectService
from app.services.task_service import TaskService


def test_project_list_is_filtered_by_current_user():
    user = SimpleNamespace(id=7)
    projects = [object(), object()]
    service = ProjectService(Mock())
    service.projects.get_by_user = Mock(return_value=projects)

    result = service.get_all(user)

    assert result == projects
    service.projects.get_by_user.assert_called_once_with(7)


def test_owner_creates_task_assigned_to_project_member():
    owner = SimpleNamespace(id=1, username="owner")
    assignee = SimpleNamespace(id=7, username="alice")
    project = SimpleNamespace(id=1, owner_id=1)
    service = TaskService(Mock())
    service.projects.get_by_id = Mock(return_value=project)
    service.members.get = Mock(return_value=object())
    service.users.get_by_id = Mock(return_value=assignee)
    service.tasks.save = Mock(
        side_effect=lambda task: (
            setattr(task, "id", 2),
            task,
        )[1]
    )
    service.notifications.create_for_users = Mock()

    result = service.create_task(
        1,
        TaskCreate(
            title="Fix login",
            description="Repair authentication",
            user_id=7,
        ),
        owner,
    )

    assert result.user_id == 7
    assert result.status == "Assigned to alice"
    service.members.get.assert_called_once_with(1, 7)
    service.notifications.create_for_users.assert_called_once_with(
        user_ids={7},
        event_type="task_assigned",
        title="Task assigned",
        message='You were assigned "Fix login"',
        resource_url="/projects/1/tasks/2",
    )


def test_owner_can_leave_new_task_unassigned():
    owner = SimpleNamespace(id=1, username="owner")
    project = SimpleNamespace(id=1, owner_id=1)
    service = TaskService(Mock())
    service.projects.get_by_id = Mock(return_value=project)
    service.members.get = Mock()
    service.tasks.save = Mock(
        side_effect=lambda task: (
            setattr(task, "id", 2),
            task,
        )[1]
    )
    service.notifications.create_for_users = Mock()

    result = service.create_task(
        1,
        TaskCreate(
            title="Fix login",
            description="Repair authentication",
        ),
        owner,
    )

    assert result.user_id is None
    assert result.status == "Not Assigned"
    service.members.get.assert_not_called()
    service.notifications.create_for_users.assert_not_called()


def test_owner_cannot_assign_task_to_non_member():
    owner = SimpleNamespace(id=1, username="owner")
    project = SimpleNamespace(id=1, owner_id=1)
    service = TaskService(Mock())
    service.projects.get_by_id = Mock(return_value=project)
    service.members.get = Mock(return_value=None)
    service.tasks.save = Mock()

    with pytest.raises(ProjectMembershipRequiredError):
        service.create_task(
            1,
            TaskCreate(
                title="Fix login",
                description="Repair authentication",
                user_id=7,
            ),
            owner,
        )

    service.tasks.save.assert_not_called()


def test_non_member_cannot_claim_task():
    user = SimpleNamespace(id=7, username="alice")
    project = SimpleNamespace(id=1, owner_id=1)
    service = TaskService(Mock())
    service.projects.get_by_id = Mock(return_value=project)
    service.members.get = Mock(return_value=None)
    service.tasks.claim = Mock()

    with pytest.raises(ProjectMembershipRequiredError):
        service.claim_task(1, 2, user)

    service.tasks.claim.assert_not_called()


def test_member_claims_task_and_owner_is_notified():
    user = SimpleNamespace(id=7, username="alice")
    project = SimpleNamespace(id=1, owner_id=1)
    unassigned_task = SimpleNamespace(id=2, user_id=None, title="Fix login")
    claimed_task = SimpleNamespace(id=2, user_id=7, title="Fix login")
    service = TaskService(Mock())
    service.projects.get_by_id = Mock(return_value=project)
    service.members.get = Mock(return_value=object())
    service.tasks.get_one_by_project = Mock(return_value=unassigned_task)
    service.tasks.claim = Mock(return_value=claimed_task)
    service.notifications.create_for_users = Mock()

    result = service.claim_task(1, 2, user)

    assert result is claimed_task
    service.tasks.claim.assert_called_once_with(
        project_id=1,
        task_id=2,
        user_id=7,
        status="Assigned to alice",
    )
    service.notifications.create_for_users.assert_called_once_with(
        user_ids={1},
        event_type="task_claimed",
        title="Task claimed",
        message='alice claimed "Fix login"',
        resource_url="/projects/1/tasks/2",
    )


def test_simultaneous_claim_loser_gets_conflict():
    user = SimpleNamespace(id=7, username="alice")
    project = SimpleNamespace(id=1, owner_id=1)
    unassigned_task = SimpleNamespace(id=2, user_id=None, title="Fix login")
    service = TaskService(Mock())
    service.projects.get_by_id = Mock(return_value=project)
    service.members.get = Mock(return_value=object())
    service.tasks.get_one_by_project = Mock(return_value=unassigned_task)
    service.tasks.claim = Mock(return_value=None)

    with pytest.raises(TaskAlreadyAssignedError):
        service.claim_task(1, 2, user)
