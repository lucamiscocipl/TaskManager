import pytest

from app.database import session_local
from app.models.projects import Project
from app.repositories.project_repository import ProjectRepository


@pytest.fixture
def db():
    session = session_local()
    try:
        yield session
    finally:
        session.close()


def test_project_repository_save_and_read(db):
    repo = ProjectRepository(db)
    project = Project(
        title="Integration Test Project",
        description="Created by integration test",
        owner_id=1,
    )

    saved = repo.save(project)
    fetched = repo.get_by_id(saved.id)

    assert fetched is not None
    assert fetched.id == saved.id
    assert fetched.title == "Integration Test Project"


def test_project_repository_get_all(db):
    repo = ProjectRepository(db)

    projects = repo.get_all()

    assert isinstance(projects, list)
    assert all(isinstance(project, Project) for project in projects)


def test_project_repository_get_by_id_returns_none_for_missing_project(db):
    repo = ProjectRepository(db)

    result = repo.get_by_id(999999)

    assert result is None
