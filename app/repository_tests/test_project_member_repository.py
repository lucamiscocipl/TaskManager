from unittest.mock import Mock

import pytest
from sqlalchemy.exc import SQLAlchemyError

from app.exceptions import ProjectMemberRepositoryError
from app.models.project_members import ProjectMember
from app.repositories.project_member_repository import ProjectMemberRepository


def test_save_calls_add_commit_and_refresh():
    db = Mock()
    repo = ProjectMemberRepository(db)
    member = object()

    result = repo.save(member)

    db.add.assert_called_once_with(member)
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(member)
    assert result is member


def test_save_rolls_back_on_error():
    db = Mock()
    db.commit.side_effect = SQLAlchemyError("db failed")
    repo = ProjectMemberRepository(db)
    member = object()

    with pytest.raises(ProjectMemberRepositoryError):
        repo.save(member)

    db.rollback.assert_called_once()


def test_get_returns_member_by_key():
    db = Mock()
    member = object()
    db.get.return_value = member
    repo = ProjectMemberRepository(db)

    result = repo.get(project_id=1, user_id=2)

    assert result is member
    db.get.assert_called_once_with(ProjectMember, (1, 2))


def test_get_by_project_returns_matching_members():
    db = Mock()
    members = [object(), object()]
    db.scalars.return_value.all.return_value = members
    repo = ProjectMemberRepository(db)

    result = repo.get_by_project(1)

    assert result == members
    db.scalars.assert_called_once()


def test_delete_calls_delete_and_commit():
    db = Mock()
    repo = ProjectMemberRepository(db)
    member = object()

    repo.delete(member)

    db.delete.assert_called_once_with(member)
    db.commit.assert_called_once()


def test_delete_rolls_back_on_error():
    db = Mock()
    db.commit.side_effect = SQLAlchemyError("db failed")
    repo = ProjectMemberRepository(db)
    member = object()

    with pytest.raises(ProjectMemberRepositoryError):
        repo.delete(member)

    db.rollback.assert_called_once()
