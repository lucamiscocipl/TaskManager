from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import selectinload

from app.exceptions import ProjectMemberRepositoryError
from app.models.project_members import ProjectMember
from app.repositories.base_repository import BaseRepository


class ProjectMemberRepository(BaseRepository):
    def save(self, project_member: ProjectMember) -> ProjectMember:
        try:
            self.db.add(project_member)
            self.db.commit()
            self.db.refresh(project_member)
        except SQLAlchemyError as error:
            self.db.rollback()
            raise ProjectMemberRepositoryError("save") from error

        return project_member

    def get(self, project_id: int, user_id: int) -> ProjectMember | None:
        try:
            return self.db.get(ProjectMember, (project_id, user_id))
        except SQLAlchemyError as error:
            self.db.rollback()
            raise ProjectMemberRepositoryError("read") from error

    def get_by_project(self, project_id: int) -> list[ProjectMember]:
        try:
            statement = (
                select(ProjectMember)
                .options(selectinload(ProjectMember.user))
                .where(ProjectMember.project_id == project_id)
                .order_by(ProjectMember.joined_at, ProjectMember.user_id)
            )
            return list(self.db.scalars(statement).all())
        except SQLAlchemyError as error:
            self.db.rollback()
            raise ProjectMemberRepositoryError("list") from error

    def delete(self, project_member: ProjectMember) -> None:
        try:
            self.db.delete(project_member)
            self.db.commit()
        except SQLAlchemyError as error:
            self.db.rollback()
            raise ProjectMemberRepositoryError("delete") from error
