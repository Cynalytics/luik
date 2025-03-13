from datetime import datetime, timedelta, timezone

import jwt
import structlog
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt import InvalidTokenError
from passlib.context import CryptContext
from pydantic import BaseModel
from starlette import status

from luik.config import settings

logger = structlog.get_logger(__name__)

ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_at: str


def get_access_token(form_data: OAuth2PasswordRequestForm) -> tuple[str, datetime]:
    # TODO: Have each kitten have their own username and password
    system_username = "username"
    hashed_password = pwd_context.hash(settings.auth_password)

    if not (
        form_data.username == system_username
        and pwd_context.verify(form_data.password, hashed_password)
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token_expiration = datetime.now(timezone.utc) + timedelta(minutes=10.0)
    access_token = jwt.encode(
        {"sub": form_data.username, "exp": token_expiration},
        "settings.secret",
        algorithm=ALGORITHM,
    )

    return access_token, token_expiration


def authenticate_token(token: str = Depends(oauth2_scheme)) -> str:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, "settings.secret", algorithms=[ALGORITHM])
        username = payload.get("sub")

        if username is None:
            raise credentials_exception

        logger.info("Authenticated user: %s", username)
        return str(username)
    except InvalidTokenError as error:
        raise credentials_exception from error
