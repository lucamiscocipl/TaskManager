from sqlalchemy.orm import Session

from app.exceptions import ProjectNotFoundError
from app.models.project_members import ProjectMember
from app.models.projects import Project
from app.models.user import User
from app.repositories.project_member_repository import ProjectMemberRepository
from app.repositories.project_repository import ProjectRepository
from app.schemas.projects import ProjectCreate


class ProjectService:
    def __init__(self, db: Session):
        self.projects = ProjectRepository(db)
        self.members = ProjectMemberRepository(db)

    def create(self, project_data: ProjectCreate, current_user: User) -> Project:
        project = Project(
            title=project_data.title,
            description=project_data.description,
            owner_id=current_user.id,
        )

        project = self.projects.save(project)

        owner_as_member = ProjectMember(
            project_id=project.id,
            user_id=current_user.id,
        )
        self.members.save(owner_as_member)

        return project

    def get_all(self) -> list[Project]:
        return self.projects.get_all()

    def get(self, project_id: int) -> Project:
        project = self.projects.get_by_id(project_id)

        if project is None:
            raise ProjectNotFoundError()

        return project
