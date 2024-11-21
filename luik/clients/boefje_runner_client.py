import datetime
import json
import uuid
from base64 import b64encode
from collections.abc import Set
from enum import Enum
from typing import Any

from httpx import Client, HTTPTransport, Response
from pydantic import AwareDatetime, BaseModel, Field, TypeAdapter
import structlog

logger = structlog.get_logger(__name__)


class BoefjeRunnerClient:
    def __init__(self, base_url: str):
        self._session = Client(base_url=base_url, transport=HTTPTransport(retries=6))

    def boefje_input(self, task_id: str) -> dict[str, Any] | None:
        response = self._session.get(f"/api/v0/tasks/{task_id}")
        response.raise_for_status()
        return TypeAdapter(dict).validate_json(response.content)
