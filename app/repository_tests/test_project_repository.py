from unittest.mock import Mock

import pytest
from sqlalchemy.exc import SQLAlchemyError

from app.exceptions import ProjectRepositoryError
from app.repositories.project_repository import ProjectRepository


def test_save_calls_add_and_commit():
    db = Mock()
    repo = ProjectRepository(db)

    project = object()
    result = repo.save(project)

    db.add.assert_called_once_with(project)
    db.commit.assert_called_once()
    assert result is project


def test_save_rolls_back_on_error():
    db = Mock()
    db.commit.side_effect = SQLAlchemyError("db failed")

    repo = ProjectRepository(db)
    project = object()
    with pytest.raises(ProjectRepositoryError):
        repo.save(project)

    db.rollback.assert_called_once()


def test_get_all_returns_all_projects():
    db = Mock()
    projects = [object(), object()]
    db.scalars.return_value.all.return_value = projects

    repo = ProjectRepository(db)
    result = repo.get_all()

    assert result == projects
    db.scalars.assert_called_once()


def test_get_all_rolls_back_on_error():
    db = Mock()
    db.scalars.side_effect = SQLAlchemyError("db failed")
    repo = ProjectRepository(db)

    with pytest.raises(ProjectRepositoryError):
        repo.get_all()

    db.rollback_assert_called_once()


def test_get_by_user_returns_member_projects():
    db = Mock()
    projects = [object(), object()]
    db.scalars.return_value.all.return_value = projects
    repo = ProjectRepository(db)

    result = repo.get_by_user(7)

    assert result == projects
    db.scalars.assert_called_once()


def test_get_by_id_returns_project():
    db = Mock()
    project = object()
    db.get.return_value = project
    repo = ProjectRepository(db)
    result = repo.get_by_id(1)

    assert result is project
    db.get.assert_called_once()
