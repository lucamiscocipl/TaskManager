from datetime import datetime, timedelta, timezone

import jwt
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import ALGORITHM, SECRET_KEY, get_current_user
from app.models.user import User
from app.schemas.tasks import TaskResponse
from app.schemas.users import TokenResponse, UserCreate, UserLogin, UserResponse
from app.services.task_service import TaskService
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])
TOKEN_EXPIRE_MINUTES = 30  # minutes


def create_access_token(username: str) -> str:
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=TOKEN_EXPIRE_MINUTES)
    token_data = {"sub": username, "exp": expires_at}
    return jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    service = UserService(db)
    return service.register(user_data)


@router.post(
    "/login",
    response_model=TokenResponse,
)
def login_user(login_data: UserLogin, db: Session = Depends(get_db)):
    service = UserService(db)
    user = service.login(login_data)
    access_token = create_access_token(user.username)

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user_id=user.id,
        username=user.username,
    )


@router.get("/me/tasks", response_model=list[TaskResponse])
def get_current_user_tasks(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    service = TaskService(db)
    return service.get_user_tasks(user_id=current_user.id)
