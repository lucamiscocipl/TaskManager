from sqlalchemy.orm import Session

from app.exceptions import (
    ProjectNotFoundError,
    ProjectOwnerRequiredError,
    TaskNotFoundError,
)
from app.models.tasks import Task
from app.models.user import User
from app.repositories.project_repository import ProjectRepository
from app.repositories.task_repository import TaskRepository
from app.schemas.tasks import TaskCreate


class TaskService:

    def __init__(self, db: Session):
        self.projects = ProjectRepository(db)
        self.tasks = TaskRepository(db)

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
            raise ProjectOwnerRequiredError(
                "Only the project owner can create tasks"
            )

        task = Task(
            title=task_data.title,
            description=task_data.description,
            status=task_data.status,
            project_id=project.id,
            user_id=None,
        )

        return self.tasks.save(task)

    def get_project_tasks(self, project_id: int) -> list[Task]:
        project = self.projects.get_by_id(project_id)

        if project is None:
            raise ProjectNotFoundError()

        return self.tasks.get_by_project(project_id)

    def get_project_task(self, project_id: int, task_id: int) -> Task:
        task = self.tasks.get_one_by_project(project_id, task_id)

        if task is None:
            raise TaskNotFoundError()
        return task

    def get_user_tasks(self, user_id: int) -> list[Task]:
        return self.tasks.get_by_user(user_id)
