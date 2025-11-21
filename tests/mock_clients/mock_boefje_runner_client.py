from luik.clients.boefje_runner_client import BoefjeRunnerClientInterface
from luik.models.api_models import BoefjeInputResponse, LuikBoefjeOutputRequest


class MockBoefjeRunnerClient(BoefjeRunnerClientInterface):
    def __init__(self, boefje_input_data: BoefjeInputResponse):
        self.boefje_input_data = boefje_input_data

    def boefje_input(self, task_id: str) -> BoefjeInputResponse | None:
        if self.boefje_input_data.task["id"] == task_id:
            return self.boefje_input_data
        return None

    def boefje_output(
        self, task_id: str, boefje_output: LuikBoefjeOutputRequest
    ) -> None:
        if self.boefje_input_data.task["id"] == task_id:
            return
        raise Exception("Mock error")
