from typing import Any

import structlog
from httpx import Client, HTTPTransport
from pydantic import TypeAdapter

logger = structlog.get_logger(__name__)


class BoefjeRunnerClient:
    def __init__(self, base_url: str):
        self._session = Client(base_url=base_url, transport=HTTPTransport(retries=6))

    def boefje_input(self, task_id: str) -> dict[str, Any] | None:
        response = self._session.get(f"/api/v0/tasks/{task_id}")
        response.raise_for_status()
        return TypeAdapter(dict).validate_json(response.content)
