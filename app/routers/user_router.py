from datetime import datetime, timedelta, timezone

import jwt
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import ALGORITHM, SECRET_KEY
from app.schemas.users import TokenResponse, UserCreate, UserLogin, UserResponse
from app.services import user_service

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
    return user_service.register_user(db=db, user_data=user_data)


@router.post(
    "/login",
    response_model=TokenResponse,
)
def login_user(login_data: UserLogin, db: Session = Depends(get_db)):
    user = user_service.login_user(db=db, login_data=login_data)
    access_token = create_access_token(user.username)

    return TokenResponse(access_token=access_token, token_type="bearer")
