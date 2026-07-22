from unittest.mock import Mock

import pytest
from sqlalchemy.exc import SQLAlchemyError

from app.exceptions import TaskRepositoryError
from app.repositories.task_repository import TaskRepository


def test_save_calls_tasks():
    db = Mock()
    repo = TaskRepository(db)
    task = object()
    result = repo.save(task)

    db.add.assert_called_once_with(task)
    db.commit.assert_called_once()
    assert result is task


def test_save_rolls_back_task():
    db = Mock()
    repo = TaskRepository(db)
    db.commit.side_effect = SQLAlchemyError("db failed")

    task = object()
    with pytest.raises(TaskRepositoryError):
        repo.save(task)
    db.rollback.assert_called_once()


def test_get_by_project_returns_list():
    db = Mock()
    repo = TaskRepository(db)
    tasks = [object(), object()]
    db.scalars.return_value.all.return_value = tasks

    result = repo.get_by_project(3)

    assert result == tasks
    db.scalars.assert_called_once()


def test_get_one_by_project_returns_task():
    db = Mock()
    task = object()
    db.scalar.return_value = task
    repo = TaskRepository(db)

    result = repo.get_one_by_project(1, 2)

    assert result is task
    db.scalar.assert_called_once()


def test_get_by_user_returns_tasks():
    db = Mock()
    tasks = [object(), object()]
    db.scalars.return_value.all.return_value = tasks
    repo = TaskRepository(db)

    result = repo.get_by_user(3)
    assert result == tasks
    db.scalars.assert_called_once()
