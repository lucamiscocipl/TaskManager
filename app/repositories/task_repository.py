from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.tasks import Task


def save_task(db: Session, task: Task) -> Task:
    db.add(task)
    db.commit()
    db.refresh(task)

    return task


def get_tasks_by_project(db: Session, project_id: int) -> list[Task]:
    statement = select(Task).where(Task.project_id == project_id).order_by(Task.id)
    return list(db.scalars(statement).all())


def get_task_by_project(db: Session, project_id: int, task_id: int) -> Task | None:
    statement = select(Task).where(Task.id == task_id, Task.project_id == project_id)
    return db.scalar(statement)


def get_tasks_by_user(db: Session, user_id: int) -> list[Task]:
    statement = select(Task).where(Task.user_id == user_id).order_by(Task.id)
    return list(db.scalars(statement).all())
