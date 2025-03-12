import json
from fastapi.testclient import TestClient
import pytest

from luik.clients.boefje_runner_client import (
    BoefjeRunnerClientInterface,
    get_boefje_runner_client,
)
from luik.clients.katalogus_client import KatalogusClientInterface, get_katalogus_client
from luik.clients.scheduler_client import (
    SchedulerClientInterface,
    get_scheduler_client,
)
from luik.clients.octopoes_client import OctopoesClientInterface, get_octopoes_client
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
    mock_scheduler_client: SchedulerClientInterface,
    mock_katalogus_client: KatalogusClientInterface,
    mock_octopoes_client: OctopoesClientInterface,
    mock_boefje_runner_client: BoefjeRunnerClientInterface,
) -> TestClient:
    from luik.server import app

    app.dependency_overrides[get_scheduler_client] = lambda: mock_scheduler_client
    app.dependency_overrides[get_katalogus_client] = lambda: mock_katalogus_client
    app.dependency_overrides[get_octopoes_client] = lambda: mock_octopoes_client
    app.dependency_overrides[get_boefje_runner_client] = (
        lambda: mock_boefje_runner_client
    )

    return TestClient(app)


@pytest.fixture
def authenticated_api(
    mock_scheduler_client: SchedulerClientInterface,
    mock_katalogus_client: KatalogusClientInterface,
    mock_octopoes_client: OctopoesClientInterface,
    mock_boefje_runner_client: BoefjeRunnerClientInterface,
) -> TestClient:
    from luik.server import app

    app.dependency_overrides[get_scheduler_client] = lambda: mock_scheduler_client
    app.dependency_overrides[get_katalogus_client] = lambda: mock_katalogus_client
    app.dependency_overrides[get_octopoes_client] = lambda: mock_octopoes_client
    app.dependency_overrides[get_boefje_runner_client] = (
        lambda: mock_boefje_runner_client
    )

    client = TestClient(app)
    response = client.post(
        "/token",
        data={"username": "settings.username", "password": "settings.password"},
    )
    print(response.json())
    token = response.json()["access_token"]
    client.headers.update({"Authorization": f"Bearer {token}"})

    return client
