import hashlib

import structlog
from fastapi import Depends, HTTPException
from fastapi.security import APIKeyHeader
from starlette import status

from luik.config import settings

logger = structlog.get_logger(__name__)

header_scheme = APIKeyHeader(
    name="luik-api-key", description="API key for Luik", auto_error=False
)


def authenticate_token(api_key: str | None = Depends(header_scheme)) -> None:
    logger.info("Authenticating API key", api_key=api_key)
    if (
        api_key is None
        or hashlib.sha256(api_key.encode(encoding="utf-8")).hexdigest()
        != settings.token_secret
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
