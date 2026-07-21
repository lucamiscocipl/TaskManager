from sqlalchemy.orm import Session

from app.exceptions import (
    ProjectMembershipRequiredError,
    ProjectNotFoundError,
    TaskCommentDeleteForbiddenError,
    TaskCommentNotFoundError,
    TaskNotFoundError,
)
from app.models.projects import Project
from app.models.task_comments import TaskComment
from app.models.tasks import Task
from app.models.user import User
from app.repositories.project_member_repository import ProjectMemberRepository
from app.repositories.project_repository import ProjectRepository
from app.repositories.task_comment_repository import TaskCommentRepository
from app.repositories.task_repository import TaskRepository
from app.schemas.task_comments import TaskCommentCreate


class TaskCommentService:
    def __init__(self, db: Session, current_user: User):
        self.current_user = current_user
        self.projects = ProjectRepository(db)
        self.members = ProjectMemberRepository(db)
        self.tasks = TaskRepository(db)
        self.comments = TaskCommentRepository(db)

    def require_task_access(
        self, project_id: int, task_id: int
    ) -> tuple[Project, Task]:
        project = self.projects.get_by_id(project_id)

        if project is None:
            raise ProjectNotFoundError()
        membership = self.members.get(project_id, self.current_user.id)
        if membership is None:
            raise ProjectMembershipRequiredError(
                "Only project memmbers can access task commments"
            )
        task = self.tasks.get_one_by_project(project_id, task_id)
        if task is None:
            raise TaskNotFoundError()

        return project, task

    def submit_comment(
        self, project_id: int, task_id: int, comment_data: TaskCommentCreate
    ) -> TaskComment:
        self.require_task_access(project_id, task_id)
        comment = TaskComment(
            task_id=task_id,
            author_id=self.current_user.id,
            content=comment_data.content,
        )
        return self.comments.save(comment)

    def list_comments(self, project_id: int, task_id: int) -> list[TaskComment]:
        self.require_task_access(project_id, task_id)
        return self.comments.get_by_task(task_id)

    def delete_comment(self, project_id: int, task_id: int, comment_id: int) -> None:
        project, _ = self.require_task_access(project_id, task_id)

        comment = self.comments.get_one(task_id, comment_id)

        if comment is None:
            raise TaskCommentNotFoundError()

        is_author = comment.author_id == self.current_user.id
        is_project_owner = project.owner_id == self.current_user.id

        if not is_author and not is_project_owner:
            raise TaskCommentDeleteForbiddenError()

        self.comments.delete(comment)
