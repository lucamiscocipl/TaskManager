from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.project_members import ProjectMember
from app.models.projects import Project
from app.models.user import User
from app.repositories import project_member_repository, project_repository
from app.schemas.projects import ProjectCreate


def create_project(
    project_data: ProjectCreate, db: Session, current_user: User
) -> Project:
    project = Project(
        title=project_data.title,
        description=project_data.description,
        owner_id=current_user.id,
    )

    project = project_repository.save_project(db=db, project=project)

    owner_as_member = ProjectMember(project_id=project.id, user_id=current_user.id)
    project_member_repository.save_project_member(db=db, project_member=owner_as_member)

    return project


def get_projects(db: Session) -> list[Project]:
    return project_repository.get_all_projects(db=db)


def get_project(project_id: int, db: Session) -> Project:
    project = project_repository.get_project_by_id(db=db, project_id=project_id)

    if project is None:
        raise HTTPException(status_code=404, detail="Project was not found")

    return project
