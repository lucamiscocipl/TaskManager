from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import defer

from app.exceptions import TaskImageRepositoryError
from app.models.task_images import TaskImage
from app.repositories.base_repository import BaseRepository


class TaskImageRepository(BaseRepository):
    def save(self, task_image: TaskImage) -> TaskImage:
        try:
            self.db.add(task_image)
            self.db.commit()
            self.db.refresh(task_image)
        except SQLAlchemyError as error:
            self.db.rollback()
            raise TaskImageRepositoryError("save") from error

        return task_image

    def get_by_task(self, task_id: int) -> list[TaskImage]:
        try:
            statement = (
                select(TaskImage)
                .where(TaskImage.task_id == task_id)
                .options(defer(TaskImage.image_data))
                .order_by(TaskImage.created_at, TaskImage.id)
            )
            return list(self.db.scalars(statement).all())
        except SQLAlchemyError as error:
            self.db.rollback()
            raise TaskImageRepositoryError("list") from error

    def get_one(self, task_id: int, image_id: int) -> TaskImage | None:
        try:
            statement = select(TaskImage).where(
                TaskImage.id == image_id,
                TaskImage.task_id == task_id,
            )
            return self.db.scalar(statement)
        except SQLAlchemyError as error:
            self.db.rollback()
            raise TaskImageRepositoryError("read") from error

    def delete(self, task_image: TaskImage) -> None:
        try:
            self.db.delete(task_image)
            self.db.commit()
        except SQLAlchemyError as error:
            self.db.rollback()
            raise TaskImageRepositoryError("delete") from error
