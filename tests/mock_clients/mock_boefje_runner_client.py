from typing import Any
from luik.clients.boefje_runner_client import BoefjeRunnerClientInterface
from luik.models.api_models import LuikBoefjeOutputRequest


class MockBoefjeRunnerClient(BoefjeRunnerClientInterface):
    def boefje_input(self, task_id: str) -> dict[str, Any]:
        raise NotImplementedError()

    def boefje_output(
        self, task_id: str, boefje_output: LuikBoefjeOutputRequest
    ) -> None:
        raise NotImplementedError()
