from typing import Annotated

from fastapi import APIRouter, Depends, File, Response, UploadFile, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.task_images import TaskImageResponse
from app.services.task_image_service import MAX_IMAGE_SIZE, TaskImageService

router = APIRouter(
    prefix="/projects/{project_id}/tasks/{task_id}/images",
    tags=["Task Images"],
)


def get_task_image_service(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TaskImageService:
    return TaskImageService(db=db, current_user=current_user)


TaskImageServiceDep = Annotated[TaskImageService, Depends(get_task_image_service)]


@router.post(
    "",
    response_model=TaskImageResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_task_image(
    project_id: int,
    task_id: int,
    service: TaskImageServiceDep,
    file: UploadFile = File(...),
):
    image_data = await file.read(MAX_IMAGE_SIZE + 1)
    filename = file.filename or "image"
    content_type = file.content_type or ""
    await file.close()

    return service.upload_image(
        project_id=project_id,
        task_id=task_id,
        filename=filename,
        content_type=content_type,
        image_data=image_data,
    )


@router.get(
    "",
    response_model=list[TaskImageResponse],
)
def list_task_images(
    project_id: int,
    task_id: int,
    service: TaskImageServiceDep,
):
    return service.list_images(
        project_id=project_id,
        task_id=task_id,
    )


@router.get("/{image_id}/content")
def get_task_image_content(
    project_id: int,
    task_id: int,
    image_id: int,
    service: TaskImageServiceDep,
):
    task_image = service.get_image(
        project_id=project_id,
        task_id=task_id,
        image_id=image_id,
    )

    return Response(
        content=task_image.image_data,
        media_type=task_image.content_type,
    )


@router.delete(
    "/{image_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_task_image(
    project_id: int,
    task_id: int,
    image_id: int,
    service: TaskImageServiceDep,
) -> None:
    service.delete_image(
        project_id=project_id,
        task_id=task_id,
        image_id=image_id,
    )
