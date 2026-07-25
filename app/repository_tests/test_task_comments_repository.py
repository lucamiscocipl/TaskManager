from unittest.mock import Mock

import pytest
from sqlalchemy.exc import SQLAlchemyError

from app.exceptions import TaskCommentRepositoryError
from app.repositories.task_comment_repository import TaskCommentRepository


def test_save_calls_add_commit_and_refresh():
    db = Mock()
    repo = TaskCommentRepository(db)
    comment = object()

    result = repo.save(comment)

    db.add.assert_called_once_with(comment)
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(comment)
    assert result is comment


def test_save_rolls_back_on_error():
    db = Mock()
    db.commit.side_effect = SQLAlchemyError("db failed")
    repo = TaskCommentRepository(db)
    comment = object()

    with pytest.raises(TaskCommentRepositoryError):
        repo.save(comment)

    db.rollback.assert_called_once()


def test_get_by_task_returns_comments():
    db = Mock()
    comments = [object(), object()]
    db.scalars.return_value.all.return_value = comments
    repo = TaskCommentRepository(db)

    result = repo.get_by_task(1)

    assert result == comments
    db.scalars.assert_called_once()


def test_get_by_tasks_rolls_back_on_error():
    db = Mock()
    db.scalars.side_effect = SQLAlchemyError("db failed")
    repo = TaskCommentRepository(db)

    with pytest.raises(TaskCommentRepositoryError):
        repo.get_by_task(1)

    db.rollback.assert_called_once()


def test_get_one_returns_comment():
    db = Mock()
    comment = object()
    db.scalar.return_value = comment
    repo = TaskCommentRepository(db)

    result = repo.get_one(1, 2)

    assert result is comment
    db.scalar.assert_called_once()


def test_get_one_rolls_back_on_error():
    db = Mock()
    db.scalar.side_effect = SQLAlchemyError("db fail")
    repo = TaskCommentRepository(db)

    with pytest.raises(TaskCommentRepositoryError):
        repo.get_one(1, 2)
    db.rollback.assert_called_once()


def test_delete_calls_delete_and_commit():
    db = Mock()
    repo = TaskCommentRepository(db)
    comment = object()

    repo.delete(comment)

    db.delete.assert_called_once_with(comment)
    db.commit.assert_called_once()


def test_delete_rolls_back_on_error():
    db = Mock()
    db.commit.side_effect = SQLAlchemyError("db failed")
    repo = TaskCommentRepository(db)
    comment = object()

    with pytest.raises(TaskCommentRepositoryError):
        repo.delete(comment)

    db.rollback.assert_called_once()
