from sqlalchemy.orm import Session

from app.models.project_members import ProjectMember


def save_project_member(db: Session, project_member: ProjectMember) -> ProjectMember:
    db.add(project_member)
    db.commit()
    db.refresh(project_member)
    return project_member
