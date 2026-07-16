import os
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import InvalidTokenError
from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import Base, engine, get_db
from app.models.projects import Project
from app.models.tasks import Task
from app.models.user import User
from app.schemas.projects import ProjectCreate, ProjectResponse
from app.schemas.tasks import TaskCreate, TaskResponse
from app.schemas.users import TokenResponse, UserCreate, UserLogin, UserResponse

app = FastAPI()

bearer_security = HTTPBearer()

Base.metadata.create_all(bind=engine)
password_hash = PasswordHash.recommended()

SECRET_KEY = os.environ["SECRET_KEY"]
ALGORITHM = "HS256"
TOKEN_EXPIRE_MINUTES = 30  # minutes


def create_access_token(username: str) -> str:
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=TOKEN_EXPIRE_MINUTES)

    token_data = {"sub": username, "exp": expires_at}

    return jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_security),
    db: Session = Depends(get_db),
) -> User:
    authentication_error = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM]
        )
        username = payload.get("sub")
        if not isinstance(username, str):
            raise authentication_error
    except InvalidTokenError:
        raise authentication_error
    statement = select(User).where(User.username == username)
    user = db.scalar(statement)

    if user is None:
        raise authentication_error
    return user


@app.get("/")
def read_root():
    return {"message": "Database tables created"}


# Projects


@app.post("/projects", response_model=ProjectResponse)
def create_project(
    project_data: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = Project(
        title=project_data.title,
        description=project_data.description,
        owner_id=current_user.id,
    )
    db.add(project)
    db.commit()
    db.refresh(project)

    return project


@app.get("/projects", response_model=list[ProjectResponse])
def get_projects(db: Session = Depends(get_db)):
    statement = select(Project).order_by(Project.id)
    return db.scalars(statement).all()


@app.get("/projects/{project_id}", response_model=ProjectResponse)
def get_project(project_id: int, db: Session = Depends(get_db)):
    project = db.get(Project, project_id)
    return project


# Users


@app.post("/users/register", response_model=UserResponse)
def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    statement = select(User).where(User.username == user_data.username)
    existing_user = db.scalar(statement)

    if existing_user is not None:
        raise HTTPException(status_code=409, detail="This user already exists")
    user = User(
        username=user_data.username,
        hashed_password=password_hash.hash(user_data.password),
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


@app.post("/users/login", response_model=TokenResponse)
def login_user(login_data: UserLogin, db: Session = Depends(get_db)):
    statement = select(User).where(User.username == login_data.username)
    user = db.scalar(statement)

    if user is None:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    password_check = password_hash.verify(login_data.password, user.hashed_password)
    if not password_check:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    access_token = create_access_token(user.username)
    return {"access_token": access_token, "token_type": "bearer"}


# Tasks


@app.post("/projects/{project_id}/tasks", response_model=TaskResponse)
def create_task(
    project_id: int,
    task_data: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = db.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    if project.owner_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Only the project owner can create tasks"
        )
    task = Task(
        title=task_data.title,
        description=task_data.description,
        status=task_data.status,
        project_id=project.id,
        user_id=None,
    )

    db.add(task)
    db.commit()
    db.refresh(task)

    return task


@app.get("/projects/{project_id}/tasks", response_model=list[TaskResponse])
def get_project_tasks(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = db.get(Project, project_id)

    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    statement = select(Task).where(Task.project_id == project_id).order_by(Task.id)
    return db.scalars(statement).all()


@app.get("/projects/{project_id}/tasks/{task_id}", response_model=TaskResponse)
def get_project_task(
    project_id: int,
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    statement = select(Task).where(Task.id == task_id, Task.project_id == project_id)
    task = db.scalar(statement)

    if task is None:
        raise HTTPException(status_code=404, detail="Task not found in this project")

    return task
