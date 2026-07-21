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
