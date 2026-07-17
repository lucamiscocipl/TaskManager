import os

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import InvalidTokenError
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories import user_repository

bearer_security = HTTPBearer()

SECRET_KEY = os.environ["SECRET_KEY"]
ALGORITHM = "HS256"


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_security),
    db: Session = Depends(get_db),
):
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
    user = user_repository.get_user_by_username(db=db, username=username)

    if user is None:
        raise authentication_error
    return user
