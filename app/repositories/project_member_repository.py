from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.project_members import ProjectMember


def save_project_member(db: Session, project_member: ProjectMember) -> ProjectMember:
    db.add(project_member)
    db.commit()
    db.refresh(project_member)
    return project_member


def get_project_member(
    db: Session, project_id: int, user_id: int
) -> ProjectMember | None:
    return db.get(ProjectMember, (project_id, user_id))


def get_project_members(db: Session, project_id: int) -> list[ProjectMember]:
    statement = (
        select(ProjectMember)
        .where(ProjectMember.project_id == project_id)
        .order_by(ProjectMember.joined_at, ProjectMember.user_id)
    )

    return list(db.scalars(statement).all())


def delete_project_member(db: Session, project_member: ProjectMember) -> None:
    db.delete(project_member)
    db.commit()
