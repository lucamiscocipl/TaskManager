from unittest.mock import Mock

import pytest
from sqlalchemy.exc import SQLAlchemyError

from app.exceptions import TaskImageRepositoryError
from app.repositories.task_image_repository import TaskImageRepository


def test_save_calls_add_commit_and_refresh():
    db = Mock()
    repo = TaskImageRepository(db)
    image = object()

    result = repo.save(image)

    db.add.assert_called_once_with(image)
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(image)
    assert result is image


def test_save_rolls_back_on_error():
    db = Mock()
    db.commit.side_effect = SQLAlchemyError("db failed")
    repo = TaskImageRepository(db)
    image = object()

    with pytest.raises(TaskImageRepositoryError):
        repo.save(image)

    db.rollback.assert_called_once()


def test_get_by_task_returns_images():
    db = Mock()
    images = [object(), object()]
    db.scalars.return_value.all.return_value = images
    repo = TaskImageRepository(db)

    result = repo.get_by_task(1)

    assert result == images
    db.scalars.assert_called_once()


def test_get_by_task_rolls_back_on_error():
    db = Mock()
    db.scalars.side_effect = SQLAlchemyError("db failed")
    repo = TaskImageRepository(db)

    with pytest.raises(TaskImageRepositoryError):
        repo.get_by_task(1)

    db.rollback.assert_called_once()


def test_get_one_returns_image():
    db = Mock()
    image = object()
    db.scalar.return_value = image
    repo = TaskImageRepository(db)

    result = repo.get_one(1, 2)

    assert result is image
    db.scalar.assert_called_once()


def test_get_one_rolls_back_on_error():
    db = Mock()
    db.scalar.side_effect = SQLAlchemyError("db failed")
    repo = TaskImageRepository(db)

    with pytest.raises(TaskImageRepositoryError):
        repo.get_one(1, 2)

    db.rollback.assert_called_once()


def test_delete_calls_delete_and_commit():
    db = Mock()
    repo = TaskImageRepository(db)
    image = object()

    repo.delete(image)

    db.delete.assert_called_once_with(image)
    db.commit.assert_called_once()


def test_delete_rolls_back_on_error():
    db = Mock()
    db.commit.side_effect = SQLAlchemyError("db failed")
    repo = TaskImageRepository(db)
    image = object()

    with pytest.raises(TaskImageRepositoryError):
        repo.delete(image)

    db.rollback.assert_called_once()
