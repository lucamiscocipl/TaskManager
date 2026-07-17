from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.projects import Project


def save_project(
    db: Session,
    project: Project,
) -> Project:
    db.add(project)
    db.commit()
    db.refresh(project)

    return project


def get_all_projects(
    db: Session,
) -> list[Project]:
    statement = select(Project).order_by(Project.id)
    return list(db.scalars(statement).all())


def get_project_by_id(db: Session, project_id: int) -> Project | None:
    return db.get(Project, project_id)
