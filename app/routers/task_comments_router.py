from typing import Annotated

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.task_comments import TaskCommentCreate, TaskCommentResponse
from app.services.task_comments_service import TaskCommentService

router = APIRouter(
    prefix="/projects/{project_id}/tasks/{task_id}/comments",
    tags=["Task Comments"],
)


def get_task_comments_service(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
) -> TaskCommentService:
    return TaskCommentService(db, current_user)


TaskCommentServiceDep = Annotated[
    TaskCommentService, Depends(get_task_comments_service)
]


@router.post(
    "", response_model=TaskCommentResponse, status_code=status.HTTP_201_CREATED
)
def submit_comment(
    project_id: int,
    task_id: int,
    comment_data: TaskCommentCreate,
    service: TaskCommentServiceDep,
):
    return service.submit_comment(project_id, task_id, comment_data)


@router.get("", response_model=list[TaskCommentResponse])
def list_comments(project_id: int, task_id: int, service: TaskCommentServiceDep):
    return service.list_comments(project_id, task_id)


@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(
    project_id: int, task_id: int, comment_id: int, service: TaskCommentServiceDep
):
    service.delete_comment(project_id, task_id, comment_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
