from sqlalchemy.orm import Session

from app.exceptions import (
    ProjectMembershipRequiredError,
    ProjectNotFoundError,
    ProjectOwnerRequiredError,
    TaskAlreadyAssignedError,
    TaskNotFoundError,
)
from app.models.projects import Project
from app.models.tasks import Task
from app.models.user import User
from app.repositories.project_member_repository import ProjectMemberRepository
from app.repositories.project_repository import ProjectRepository
from app.repositories.task_repository import TaskRepository
from app.repositories.user_repository import UserRepository
from app.schemas.tasks import TaskCreate
from app.services.notification_service import NotificationService


class TaskService:

    def __init__(self, db: Session):
        self.members = ProjectMemberRepository(db)
        self.notifications = NotificationService(db)
        self.projects = ProjectRepository(db)
        self.tasks = TaskRepository(db)
        self.users = UserRepository(db)

    def require_project_membership(
        self,
        project_id: int,
        current_user: User,
    ) -> Project:
        project = self.projects.get_by_id(project_id)

        if project is None:
            raise ProjectNotFoundError()
        if self.members.get(project_id, current_user.id) is None:
            raise ProjectMembershipRequiredError(
                "Only project members can access tasks"
            )

        return project

    def create_task(
        self,
        project_id: int,
        task_data: TaskCreate,
        current_user: User,
    ) -> Task:
        project = self.projects.get_by_id(project_id)

        if project is None:
            raise ProjectNotFoundError()
        if project.owner_id != current_user.id:
            raise ProjectOwnerRequiredError("Only the project owner can create tasks")

        assigned_user = None
        if task_data.user_id is not None:
            if self.members.get(project_id, task_data.user_id) is None:
                raise ProjectMembershipRequiredError(
                    "Tasks can only be assigned to project members"
                )
            assigned_user = self.users.get_by_id(task_data.user_id)

        status = (
            f"Assigned to {assigned_user.username}"
            if assigned_user is not None
            else "Not Assigned"
        )
        task = Task(
            title=task_data.title,
            description=task_data.description,
            status=status,
            project_id=project.id,
            user_id=assigned_user.id if assigned_user is not None else None,
        )

        saved_task = self.tasks.save(task)

        if assigned_user is not None and assigned_user.id != current_user.id:
            self.notifications.create_for_users(
                user_ids={assigned_user.id},
                event_type="task_assigned",
                title="Task assigned",
                message=f'You were assigned "{saved_task.title}"',
                resource_url=f"/projects/{project_id}/tasks/{saved_task.id}",
            )

        return saved_task

    def get_project_tasks(
        self,
        project_id: int,
        current_user: User,
    ) -> list[Task]:
        self.require_project_membership(project_id, current_user)
        return self.tasks.get_by_project(project_id)

    def get_project_task(
        self,
        project_id: int,
        task_id: int,
        current_user: User,
    ) -> Task:
        self.require_project_membership(project_id, current_user)
        task = self.tasks.get_one_by_project(project_id, task_id)

        if task is None:
            raise TaskNotFoundError()
        return task

    def claim_task(
        self,
        project_id: int,
        task_id: int,
        current_user: User,
    ) -> Task:
        project = self.require_project_membership(project_id, current_user)
        task = self.tasks.get_one_by_project(project_id, task_id)

        if task is None:
            raise TaskNotFoundError()
        if task.user_id is not None:
            raise TaskAlreadyAssignedError()

        claimed_task = self.tasks.claim(
            project_id=project_id,
            task_id=task_id,
            user_id=current_user.id,
            status=f"Assigned to {current_user.username}",
        )
        if claimed_task is None:
            raise TaskAlreadyAssignedError()

        recipient_ids = {project.owner_id}
        recipient_ids.discard(current_user.id)
        if recipient_ids:
            self.notifications.create_for_users(
                user_ids=recipient_ids,
                event_type="task_claimed",
                title="Task claimed",
                message=(f'{current_user.username} claimed "{claimed_task.title}"'),
                resource_url=f"/projects/{project_id}/tasks/{task_id}",
            )

        return claimed_task

    def get_user_tasks(self, user_id: int) -> list[Task]:
        return self.tasks.get_by_user(user_id)
