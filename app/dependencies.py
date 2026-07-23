import os
from pathlib import Path

import jwt
from dotenv import load_dotenv
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import InvalidTokenError
from sqlalchemy.orm import Session

from app.database import get_db
from app.exceptions import TokenValidationError
from app.repositories.user_repository import UserRepository

bearer_security = HTTPBearer()

ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env")

SECRET_KEY = os.getenv("SECRET_KEY", "")
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY is not set")

ALGORITHM = "HS256"


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_security),
    db: Session = Depends(get_db),
):
    try:
        payload = jwt.decode(
            credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM]
        )
        username = payload.get("sub")
        if not isinstance(username, str):
            raise TokenValidationError()
    except InvalidTokenError as error:
        raise TokenValidationError() from error
    users = UserRepository(db)
    user = users.get_by_username(username)

    if user is None:
        raise TokenValidationError()
    return user
