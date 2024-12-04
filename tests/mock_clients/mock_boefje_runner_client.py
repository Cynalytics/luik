from typing import Any
from luik.clients.boefje_runner_client import BoefjeRunnerClientInterface
from luik.models.api_models import LuikBoefjeOutputRequest


class MockBoefjeRunnerClient(BoefjeRunnerClientInterface):
    def __init__(self, boefje_input_data: dict[str, Any]):
        self.boefje_input_data = boefje_input_data

    def boefje_input(self, task_id: str) -> dict[str, Any]:
        if self.boefje_input_data["task_id"] == task_id:
            return self.boefje_input_data
        raise Exception("Something went wrong with `boefje_input`")

    def boefje_output(
        self, task_id: str, boefje_output: LuikBoefjeOutputRequest
    ) -> None:
        raise NotImplementedError()
