from fastapi import HTTPException
from pwdlib import PasswordHash
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories import user_repository
from app.schemas.users import UserCreate, UserLogin

password_hash = PasswordHash.recommended()


def register_user(db: Session, user_data: UserCreate) -> User:
    existing_user = user_repository.get_user_by_username(
        db=db, username=user_data.username
    )

    if existing_user is not None:
        raise HTTPException(status_code=409, detail="This user already exists")

    user = User(
        username=user_data.username,
        hashed_password=password_hash.hash(user_data.password),
    )

    return user_repository.save_user(db=db, user=user)


def login_user(db: Session, login_data: UserLogin) -> User:
    user = user_repository.get_user_by_username(db=db, username=login_data.username)

    if user is None:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    password_check = password_hash.verify(login_data.password, user.hashed_password)
    if not password_check:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    return user
