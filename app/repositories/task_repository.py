from sqlalchemy import select, update
from sqlalchemy.exc import SQLAlchemyError

from app.exceptions import TaskRepositoryError
from app.models.tasks import Task
from app.repositories.base_repository import BaseRepository


class TaskRepository(BaseRepository):
    def save(self, task: Task) -> Task:
        try:
            self.db.add(task)
            self.db.commit()
            self.db.refresh(task)
        except SQLAlchemyError as error:
            self.db.rollback()
            raise TaskRepositoryError("save") from error

        return task

    def get_by_project(self, project_id: int) -> list[Task]:
        try:
            statement = (
                select(Task).where(Task.project_id == project_id).order_by(Task.id)
            )
            return list(self.db.scalars(statement).all())
        except SQLAlchemyError as error:
            self.db.rollback()
            raise TaskRepositoryError("list") from error

    def get_one_by_project(self, project_id: int, task_id: int) -> Task | None:
        try:
            statement = select(Task).where(
                Task.id == task_id,
                Task.project_id == project_id,
            )
            return self.db.scalar(statement)
        except SQLAlchemyError as error:
            self.db.rollback()
            raise TaskRepositoryError("read") from error

    def get_by_user(self, user_id: int) -> list[Task]:
        try:
            statement = select(Task).where(Task.user_id == user_id).order_by(Task.id)
            return list(self.db.scalars(statement).all())
        except SQLAlchemyError as error:
            self.db.rollback()
            raise TaskRepositoryError("list") from error

    def claim(
        self,
        project_id: int,
        task_id: int,
        user_id: int,
        status: str,
    ) -> Task | None:
        try:
            statement = (
                update(Task)
                .where(
                    Task.id == task_id,
                    Task.project_id == project_id,
                    Task.user_id.is_(None),
                )
                .values(
                    user_id=user_id,
                    status=status,
                )
                .returning(Task)
            )
            task = self.db.scalar(statement)
            if task is None:
                self.db.rollback()
                return None

            self.db.commit()
            self.db.refresh(task)
            return task
        except SQLAlchemyError as error:
            self.db.rollback()
            raise TaskRepositoryError("claim") from error
