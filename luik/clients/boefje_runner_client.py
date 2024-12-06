from typing import Any

import structlog
from httpx import Client, HTTPTransport
from pydantic import TypeAdapter

from luik.models.api_models import LuikBoefjeOutputRequest

logger = structlog.get_logger(__name__)


class BoefjeRunnerClientInterface:
    def boefje_input(self, task_id: str) -> dict[str, Any]:
        raise NotImplementedError()

    def boefje_output(
        self, task_id: str, boefje_output: LuikBoefjeOutputRequest
    ) -> None:
        raise NotImplementedError()


class BoefjeRunnerClient(BoefjeRunnerClientInterface):
    def __init__(self, base_url: str):
        self._session = Client(base_url=base_url, transport=HTTPTransport(retries=6))

    def boefje_input(self, task_id: str) -> dict[str, str]:
        response = self._session.get(f"/api/v0/tasks/{task_id}")
        response.raise_for_status()

        return TypeAdapter(dict[str, Any]).validate_json(response.content)

    def boefje_output(
        self, task_id: str, boefje_output: LuikBoefjeOutputRequest
    ) -> None:
        response = self._session.post(
            f"/api/v0/tasks/{task_id}", json=boefje_output.model_dump()
        )
        if response.is_error:
            logger.error(response.text)
        response.raise_for_status()
