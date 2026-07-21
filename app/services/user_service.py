from pwdlib import PasswordHash
from sqlalchemy.orm import Session

from app.exceptions import InvalidCredentialsError, UsernameAlreadyExistsError
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.users import UserCreate, UserLogin

password_hash = PasswordHash.recommended()


class UserService:
    def __init__(self, db: Session):
        self.users = UserRepository(db)

    def register(self, user_data: UserCreate) -> User:
        existing_user = self.users.get_by_username(user_data.username)

        if existing_user is not None:
            raise UsernameAlreadyExistsError()

        user = User(
            username=user_data.username,
            hashed_password=password_hash.hash(user_data.password),
        )

        return self.users.save(user)

    def login(self, login_data: UserLogin) -> User:
        user = self.users.get_by_username(login_data.username)

        if user is None:
            raise InvalidCredentialsError()

        password_check = password_hash.verify(
            login_data.password,
            user.hashed_password,
        )
        if not password_check:
            raise InvalidCredentialsError()

        return user
