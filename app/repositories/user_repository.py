from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from app.exceptions import UserRepositoryError
from app.models.user import User
from app.repositories.base_repository import BaseRepository


class UserRepository(BaseRepository):
    def save(self, user: User) -> User:
        try:
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
        except SQLAlchemyError as error:
            self.db.rollback()
            raise UserRepositoryError("save") from error

        return user

    def get_by_username(self, username: str) -> User | None:
        try:
            statement = select(User).where(User.username == username)
            return self.db.scalar(statement)
        except SQLAlchemyError as error:
            self.db.rollback()
            raise UserRepositoryError("read") from error

    def get_by_id(self, user_id: int) -> User | None:
        try:
            return self.db.get(User, user_id)
        except SQLAlchemyError as error:
            self.db.rollback()
            raise UserRepositoryError("read") from error
