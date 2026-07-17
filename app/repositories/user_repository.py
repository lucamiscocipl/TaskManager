from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User


def save_user(db: Session, user: User) -> User:
    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def get_user_by_username(db: Session, username: str) -> User | None:
    statement = select(User).where(User.username == username)
    return db.scalar(statement)


def get_user_by_id(db: Session, user_id: int) -> User | None:
    return db.get(User, user_id)
