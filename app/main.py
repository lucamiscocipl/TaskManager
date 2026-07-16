import os
from datetime import datetime, timedelta, timezone

import jwt
from pwdlib import PasswordHash
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import InvalidTokenError


from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.database import Base, engine, get_db
from app.models.user import User
from app.models.tasks import Task
from app.schemas.projects import projectResponse, projectCreate
from app.models.projects import Project
from app.schemas.tasks import taskCreate, taskResponse

from app.schemas.users import tokenResponse, userCreate, userLogin, userResponse

app = FastAPI()

bearerSecurity = HTTPBearer()

Base.metadata.create_all(bind=engine)
passwordHash = PasswordHash.recommended()

secretKey = os.environ["SECRET_KEY"]
algorithm = "HS256"
tokenExpire = 30 #minutes

def createAT (username: str) -> str:
    expiresAt = datetime.now(timezone.utc) + timedelta(minutes=tokenExpire)
    
    tokenData= {
        "sub": username,
        "exp": expiresAt
    }
    
    return jwt.encode (tokenData, secretKey, algorithm=algorithm)

def get_current_user (
    credentials: HTTPAuthorizationCredentials = Depends(bearerSecurity),
    db : Session = Depends(get_db)
) -> User:
    authenticationError = HTTPException(
        status_code=401,
        detail= "Could not validate credentials",
        headers= {"WWW-Authenticate": "Bearer"}
    )
    try: 
        payload = jwt.decode (
            credentials.credentials, 
            secretKey,
            algorithms=[algorithm]
        )
        username = payload.get("sub")
        if not isinstance(username, str):
            raise authenticationError
    except InvalidTokenError:
        raise authenticationError
    statement= select(User).where(User.username == username)
    user = db.scalar(statement)
    
    if user is None:
        raise authenticationError
    return user
@app.get("/")
def read_root():
    return {"message": "Database tables created"}

                                        #Projects


@app.post("/projects", response_model=projectResponse)
def create_project (project_data: projectCreate, db: Session = Depends(get_db), current_user: User= Depends(get_current_user)):
    project = Project (
        title= project_data.title,
        description= project_data.description,
        owner_id = current_user.id
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    
    return project

@app.get("/projects", response_model=list[projectResponse])
def get_projects (db: Session = Depends(get_db)):
    statement = select(Project).order_by(Project.id)
    return db.scalars(statement).all()


@app.get("/projects/{project_id}", response_model=projectResponse)
def get_project(project_id:int , db: Session = Depends(get_db)):
    project = db.get(Project, project_id)
    return project




                                        #USERS

@app.post("/users/register", response_model=userResponse)
def registerUser (user_data: userCreate, db: Session = Depends(get_db)):
    statement = select(User).where(User.username == user_data.username)
    existingUser = db.scalar(statement)
    
    if existingUser is not None:
        raise HTTPException(
            status_code=409,
            detail="This user already exists"
        )
    user = User (
        username = user_data.username,
        hashed_password = passwordHash.hash(user_data.password)
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user

@app.post ("/users/login", response_model=tokenResponse)
def loginUser (
    login_data: userLogin,
    db: Session = Depends(get_db)
):
    statement = select(User).where (User.username == login_data.username)
    user = db.scalar(statement)
    
    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )
   
    passwordCheck = passwordHash.verify(login_data.password, user.hashed_password)
    if not passwordCheck:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )
    
    access_token = createAT(user.username)
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

                                            #TASKS
                                        
@app.post ("/projects/{project_id}/tasks", response_model= taskResponse)        
def createTask(
    project_id: int,
    task_data: taskCreate,
    db:Session= Depends(get_db),
    current_user= Depends(get_current_user)
):
    project = db.get(Project, project_id)
    if project is None:
        raise HTTPException(
            status_code= 404,
            detail= "Project not found"
        )
        
    if project.owner_id != current_user.id:
        raise HTTPException (
            status_code= 403,
            detail= "Only the project owner can create tasks"
        )
    task = Task (
        title = task_data.title,
        description= task_data.description,
        status=task_data.status,
        project_id= project.id,
        user_id = None
    )
    
    db.add(task)
    db.commit()
    db.refresh(task)
    
    return task

@app.get("/projects/{project_id}/tasks", response_model=list[taskResponse])
def get_project_tasks(
    project_id: int,
    db: Session = Depends(get_db),
   current_user: User = Depends(get_current_user)
):
        project = db.get(Project, project_id)
        
        if project is None:
            raise HTTPException(
                status_code= 404,
                detail= "Project not found"
            )
        statement = (select(Task).where(Task.project_id == project_id).order_by(Task.id))
        return db.scalars(statement).all()
@app.get("/projects/{project_id}/tasks/{task_id}", response_model=taskResponse)
def get_project_task(
    project_id: int,
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    statement = select(Task).where(Task.id == task_id, Task.project_id == project_id)
    task = db.scalar(statement)

    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Task not found in this project"
        )

    return task