from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from app.exceptions import ProjectRepositoryError
from app.models.projects import Project
from app.repositories.base_repository import BaseRepository


class ProjectRepository(BaseRepository):
    def save(self, project: Project) -> Project:
        try:
            self.db.add(project)
            self.db.commit()
            self.db.refresh(project)
        except SQLAlchemyError as error:
            self.db.rollback()
            raise ProjectRepositoryError("save") from error

        return project

    def get_all(self) -> list[Project]:
        try:
            statement = select(Project).order_by(Project.id)
            return list(self.db.scalars(statement).all())
        except SQLAlchemyError as error:
            self.db.rollback()
            raise ProjectRepositoryError("list") from error

    def get_by_id(self, project_id: int) -> Project | None:
        try:
            return self.db.get(Project, project_id)
        except SQLAlchemyError as error:
            self.db.rollback()
            raise ProjectRepositoryError("read") from error
