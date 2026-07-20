from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.project_members import ProjectMemberCreate, ProjectMemberResponse
from app.services import project_member_service

router = APIRouter(prefix="/projects/{project_id}/members", tags=["Project Members"])


@router.post(
    "", response_model=ProjectMemberResponse, status_code=status.HTTP_201_CREATED
)
def add_project_member(
    project_id: int,
    member_data: ProjectMemberCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return project_member_service.add_project_member(
        db=db,
        project_id=project_id,
        user_id=member_data.user_id,
        current_user=current_user,
    )


@router.get("", response_model=list[ProjectMemberResponse])
def get_project_members(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return project_member_service.get_project_members(
        db=db, project_id=project_id, current_user=current_user
    )


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_project_member(
    project_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    project_member_service.remove_project_member(
        db=db, project_id=project_id, user_id=user_id, current_user=current_user
    )
