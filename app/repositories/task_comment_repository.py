from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from app.exceptions import TaskCommentRepositoryError
from app.models.task_comments import TaskComment
from app.repositories.base_repository import BaseRepository


class TaskCommentRepository(BaseRepository):
    def save(self, comment: TaskComment) -> TaskComment:
        try:
            self.db.add(comment)
            self.db.commit()
            self.db.refresh(comment)
            return comment
        except SQLAlchemyError as error:
            self.db.rollback()
            raise TaskCommentRepositoryError("save") from error

    def get_by_task(self, task_id: int) -> list[TaskComment]:
        try:
            statement = (
                select(TaskComment)
                .where(TaskComment.task_id == task_id)
                .order_by(TaskComment.created_at, TaskComment.id)
            )
            return list(self.db.scalars(statement).all())
        except SQLAlchemyError as error:
            self.db.rollback()
            raise TaskCommentRepositoryError("list") from error

    def get_one(self, task_id: int, comment_id: int) -> TaskComment | None:
        try:
            statement = select(TaskComment).where(
                TaskComment.task_id == task_id, TaskComment.id == comment_id
            )
            return self.db.scalar(statement)
        except SQLAlchemyError as error:
            self.db.rollback()
            raise TaskCommentRepositoryError("read") from error

    def delete(self, comment: TaskComment) -> None:
        try:
            self.db.delete(comment)
            self.db.commit()
        except SQLAlchemyError as error:
            self.db.rollback()
            raise TaskCommentRepositoryError("delete") from error
