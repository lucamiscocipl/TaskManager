from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.project_members import ProjectMember
from app.models.projects import Project
from app.models.user import User
from app.repositories import (
    project_member_repository,
    project_repository,
    user_repository,
)


def get_project_or_404(db: Session, project_id: int) -> Project:
    project = project_repository.get_project_by_id(db=db, project_id=project_id)

    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
        )

    return project


def require_project_owner(project: Project, current_user: User) -> None:
    if project.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the project owner can manage members",
        )


def add_project_member(
    db: Session, project_id: int, user_id: int, current_user: User
) -> ProjectMember:
    project = get_project_or_404(db=db, project_id=project_id)
    require_project_owner(project=project, current_user=current_user)

    user = user_repository.get_user_by_id(db=db, user_id=user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    existing_member = project_member_repository.get_project_member(
        db=db, project_id=project_id, user_id=user_id
    )

    if existing_member is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User is already a project member",
        )

    project_member = ProjectMember(project_id=project_id, user_id=user_id)

    return project_member_repository.save_project_member(
        db=db, project_member=project_member
    )


def get_project_members(
    db: Session, project_id: int, current_user: User
) -> list[ProjectMember]:
    get_project_or_404(db=db, project_id=project_id)

    current_membership = project_member_repository.get_project_member(
        db=db, project_id=project_id, user_id=current_user.id
    )

    if current_membership is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only project members can view members",
        )

    return project_member_repository.get_project_members(db=db, project_id=project_id)


def remove_project_member(
    db: Session, project_id: int, user_id: int, current_user: User
) -> None:
    project = get_project_or_404(db=db, project_id=project_id)
    require_project_owner(project=project, current_user=current_user)

    if user_id == project.owner_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The project owner cannot be removed",
        )

    project_member = project_member_repository.get_project_member(
        db=db, project_id=project_id, user_id=user_id
    )

    if project_member is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project member not found",
        )

    project_member_repository.delete_project_member(
        db=db,
        project_member=project_member,
    )
