import json
from fastapi.testclient import TestClient
import pytest

from luik.api import (
    get_boefje_runner_client,
    get_katalogus_client,
    get_octopoes_client,
    get_scheduler_client,
)
from luik.clients.boefje_runner_client import BoefjeRunnerClientInterface
from luik.clients.katalogus_client import KatalogusClientInterface
from luik.clients.octopoes_client import OctopoesClientInterface
from luik.clients.scheduler_client import SchedulerClientInterface
from tests.mock_clients.mock_boefje_runner_client import MockBoefjeRunnerClient
from tests.mock_clients.mock_katalogus_client import MockKatalogusClient
from tests.mock_clients.mock_octopoes_client import MockOctopoesClient
from tests.mock_clients.mock_scheduler_client import MockSchedulerClient


@pytest.fixture
def mock_scheduler_client() -> SchedulerClientInterface:
    with open("./tests/mock_data/mock_pop_data.json") as f:
        data = f.read()
    return MockSchedulerClient(json.loads(data))


@pytest.fixture
def mock_katalogus_client() -> KatalogusClientInterface:
    return MockKatalogusClient()


@pytest.fixture
def mock_octopoes_client() -> OctopoesClientInterface:
    return MockOctopoesClient()


@pytest.fixture
def mock_boefje_runner_client() -> BoefjeRunnerClientInterface:
    with open("./tests/mock_data/mock_boefje_input.json") as f:
        data = f.read()
    return MockBoefjeRunnerClient(json.loads(data))


@pytest.fixture
def api(
    mock_scheduler_client,
    mock_katalogus_client,
    mock_octopoes_client,
    mock_boefje_runner_client,
):
    from luik.api import app

    app.dependency_overrides[get_scheduler_client] = lambda: mock_scheduler_client
    app.dependency_overrides[get_katalogus_client] = lambda: mock_katalogus_client
    app.dependency_overrides[get_octopoes_client] = lambda: mock_octopoes_client
    app.dependency_overrides[get_boefje_runner_client] = (
        lambda: mock_boefje_runner_client
    )

    return TestClient(app)
