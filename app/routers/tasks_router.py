from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.tasks import TaskCreate, TaskResponse
from app.services.task_service import TaskService

router = APIRouter(
    prefix="/projects",
    tags=["Tasks"],
)


@router.post(
    "/{project_id}/tasks",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_task(
    project_id: int,
    task_data: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = TaskService(db)

    return service.create_task(
        project_id=project_id,
        task_data=task_data,
        current_user=current_user,
    )


@router.get(
    "/{project_id}/tasks",
    response_model=list[TaskResponse],
)
def get_project_tasks(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = TaskService(db)

    return service.get_project_tasks(
        project_id=project_id,
        current_user=current_user,
    )


@router.get(
    "/{project_id}/tasks/{task_id}",
    response_model=TaskResponse,
)
def get_project_task(
    project_id: int,
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = TaskService(db)

    return service.get_project_task(
        project_id=project_id,
        task_id=task_id,
        current_user=current_user,
    )


@router.patch(
    "/{project_id}/tasks/{task_id}/claim",
    response_model=TaskResponse,
)
def claim_task(
    project_id: int,
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = TaskService(db)
    return service.claim_task(
        project_id=project_id,
        task_id=task_id,
        current_user=current_user,
    )
