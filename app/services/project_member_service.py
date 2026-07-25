from sqlalchemy.orm import Session

from app.exceptions import (
    ProjectMemberAlreadyExistsError,
    ProjectMemberNotFoundError,
    ProjectMembershipRequiredError,
    ProjectNotFoundError,
    ProjectOwnerRemovalError,
    ProjectOwnerRequiredError,
    UserNotFoundError,
)
from app.models.project_members import ProjectMember
from app.models.projects import Project
from app.models.user import User
from app.repositories.project_member_repository import ProjectMemberRepository
from app.repositories.project_repository import ProjectRepository
from app.repositories.user_repository import UserRepository


class ProjectMemberService:
    def __init__(self, db: Session):
        self.projects = ProjectRepository(db)
        self.members = ProjectMemberRepository(db)
        self.users = UserRepository(db)

    def get_project_or_404(self, project_id: int) -> Project:
        project = self.projects.get_by_id(project_id)

        if project is None:
            raise ProjectNotFoundError()

        return project

    @staticmethod
    def require_project_owner(project: Project, current_user: User) -> None:
        if project.owner_id != current_user.id:
            raise ProjectOwnerRequiredError("Only the project owner can manage members")

    def add(
        self,
        project_id: int,
        user_id: int,
        current_user: User,
    ) -> ProjectMember:
        project = self.get_project_or_404(project_id)
        self.require_project_owner(project, current_user)

        if self.users.get_by_id(user_id) is None:
            raise UserNotFoundError()

        if self.members.get(project_id, user_id) is not None:
            raise ProjectMemberAlreadyExistsError()

        project_member = ProjectMember(
            project_id=project_id,
            user_id=user_id,
        )
        return self.members.save(project_member)

    def get_all(
        self,
        project_id: int,
        current_user: User,
    ) -> list[ProjectMember]:
        self.get_project_or_404(project_id)

        if self.members.get(project_id, current_user.id) is None:
            raise ProjectMembershipRequiredError(
                "Only project members can view members"
            )

        return self.members.get_by_project(project_id)

    def remove(
        self,
        project_id: int,
        user_id: int,
        current_user: User,
    ) -> None:
        project = self.get_project_or_404(project_id)
        self.require_project_owner(project, current_user)

        if user_id == project.owner_id:
            raise ProjectOwnerRemovalError()

        project_member = self.members.get(project_id, user_id)
        if project_member is None:
            raise ProjectMemberNotFoundError()

        self.members.delete(project_member)
