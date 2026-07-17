from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.tasks import Task
from app.models.user import User
from app.repositories import project_repository, task_repository
from app.schemas.tasks import TaskCreate


class TaskService:

    def __init__(self, db: Session):
        self.db = db

    def create_task(
        self,
        project_id: int,
        task_data: TaskCreate,
        current_user: User,
    ) -> Task:
        project = project_repository.get_project_by_id(
            db=self.db, project_id=project_id
        )

        if project is None:
            raise HTTPException(status_code=404, detail="Project not found")
        if project.owner_id != current_user.id:
            raise HTTPException(
                status_code=403, detail="Only the project owner can create tasks"
            )

        task = Task(
            title=task_data.title,
            description=task_data.description,
            status=task_data.status,
            project_id=project.id,
            user_id=None,
        )

        return task_repository.save_task(db=self.db, task=task)

    def get_project_tasks(self, project_id: int) -> list[Task]:
        project = project_repository.get_project_by_id(
            db=self.db, project_id=project_id
        )

        if project is None:
            raise HTTPException(status_code=404, detail="Project not found")

        return task_repository.get_tasks_by_project(db=self.db, project_id=project_id)

    def get_project_task(self, project_id: int, task_id: int) -> Task:
        task = task_repository.get_task_by_project(
            db=self.db, project_id=project_id, task_id=task_id
        )

        if task is None:
            raise HTTPException(
                status_code=404, detail="Task not found in this project"
            )
        return task
