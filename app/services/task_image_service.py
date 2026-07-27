from sqlalchemy.orm import Session

from app.exceptions import (
    EmptyImageError,
    ImageTooLargeError,
    ProjectMembershipRequiredError,
    ProjectNotFoundError,
    TaskImageDeleteForbiddenError,
    TaskImageNotFoundError,
    TaskNotFoundError,
    UnsupportedImageTypeError,
)
from app.models.projects import Project
from app.models.task_images import TaskImage
from app.models.tasks import Task
from app.models.user import User
from app.repositories.project_member_repository import ProjectMemberRepository
from app.repositories.project_repository import ProjectRepository
from app.repositories.task_image_repository import TaskImageRepository
from app.repositories.task_repository import TaskRepository
from app.services.notification_service import NotificationService

ALLOWED_IMAGE_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
}

MAX_IMAGE_SIZE = 5 * 1024 * 1024


class TaskImageService:
    def __init__(self, db: Session, current_user: User):
        self.current_user = current_user
        self.notifications = NotificationService(db)
        self.projects = ProjectRepository(db)
        self.members = ProjectMemberRepository(db)
        self.tasks = TaskRepository(db)
        self.images = TaskImageRepository(db)

    def require_task_access(
        self,
        project_id: int,
        task_id: int,
    ) -> tuple[Project, Task]:
        project = self.projects.get_by_id(project_id)

        if project is None:
            raise ProjectNotFoundError()

        membership = self.members.get(project_id, self.current_user.id)
        if membership is None:
            raise ProjectMembershipRequiredError(
                "Only project members can access task images"
            )
        task = self.tasks.get_one_by_project(project_id, task_id)
        if task is None:
            raise TaskNotFoundError()

        return project, task

    def upload_image(
        self,
        project_id: int,
        task_id: int,
        filename: str,
        content_type: str,
        image_data: bytes,
    ) -> TaskImage:
        project, task = self.require_task_access(project_id, task_id)

        if content_type not in ALLOWED_IMAGE_TYPES:
            raise UnsupportedImageTypeError()

        if not image_data:
            raise EmptyImageError()

        if len(image_data) > MAX_IMAGE_SIZE:
            raise ImageTooLargeError()

        task_image = TaskImage(
            task_id=task_id,
            uploader_id=self.current_user.id,
            original_filename=filename[:255] or "image",
            content_type=content_type,
            size_bytes=len(image_data),
            image_data=image_data,
        )

        saved_image = self.images.save(task_image)

        recipient_ids = {project.owner_id}
        if task.user_id is not None:
            recipient_ids.add(task.user_id)
        recipient_ids.discard(self.current_user.id)

        if recipient_ids:
            self.notifications.create_for_users(
                user_ids=recipient_ids,
                event_type="task_image",
                title="New task image",
                message=(
                    f"{self.current_user.username} uploaded "
                    f'"{saved_image.original_filename}" to "{task.title}"'
                ),
                resource_url=f"/projects/{project_id}/tasks/{task_id}",
            )

        return saved_image

    def list_images(
        self,
        project_id: int,
        task_id: int,
    ) -> list[TaskImage]:
        self.require_task_access(project_id, task_id)

        return self.images.get_by_task(task_id)

    def get_image(self, project_id: int, task_id: int, image_id: int) -> TaskImage:
        self.require_task_access(project_id, task_id)

        task_image = self.images.get_one(task_id, image_id)

        if task_image is None:
            raise TaskImageNotFoundError()

        return task_image

    def delete_image(self, project_id: int, task_id: int, image_id: int) -> None:
        project, _ = self.require_task_access(project_id, task_id)

        task_image = self.images.get_one(task_id, image_id)

        if task_image is None:
            raise TaskImageNotFoundError()

        is_uploader = task_image.uploader_id == self.current_user.id
        is_project_owner = project.owner_id == self.current_user.id

        if not is_uploader and not is_project_owner:
            raise TaskImageDeleteForbiddenError()

        self.images.delete(task_image)
