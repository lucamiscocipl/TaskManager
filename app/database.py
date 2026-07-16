from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DATABASE_URL = "postgresql+psycopg://postgres:12345@localhost:5432/TaskManager"

engine = create_engine(
    DATABASE_URL,
)


session_local = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    with session_local() as db:
        yield db
