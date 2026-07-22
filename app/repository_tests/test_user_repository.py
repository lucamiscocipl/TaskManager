from unittest.mock import Mock

import pytest
from sqlalchemy.exc import SQLAlchemyError

from app.exceptions import UserRepositoryError
from app.repositories.user_repository import UserRepository


def test_save_calls_user():
    db = Mock()
    repo = UserRepository(db)
    user = object()
    result = repo.save(user)

    db.add.assert_called_once_with(user)
    db.commit.assert_called_once()
    assert result is user


def test_save_rolls_back_user():
    db = Mock()
    repo = UserRepository(db)
    db.commit.side_effect = SQLAlchemyError("db failed")

    user = object()
    with pytest.raises(UserRepositoryError):
        repo.save(user)

    db.rollback.assert_called_once()


def test_get_by_username_returns_user():
    db = Mock()
    repo = UserRepository(db)
    user = object()
    db.scalar.return_value = user

    result = repo.get_by_username("luca")

    assert result is user
    db.scalar.assert_called_once()


def test_get_by_id_returns_user():
    db = Mock()
    repo = UserRepository(db)
    user = object()
    db.get.return_value = user
    result = repo.get_by_id(1)

    assert result is user
    db.get.assert_called_once()
