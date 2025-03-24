import json
import os
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

PLACEHOLDER_URL = "http://localhost:0"
HASHED_PASSWORD = "10a6e6cc8311a3e2bcc09bf6c199adecd5dd59408c343e926b129c4914f3cb01"  # "test_password" hashed




@pytest.fixture
def full_mock_scheduler_client() -> SchedulerClientInterface:
    with open("./tests/mock_data/mock_pop_data.json") as f:
        data = f.read()
    return MockSchedulerClient(json.loads(data))


@pytest.fixture
def empty_mock_scheduler_client() -> SchedulerClientInterface:
    return MockSchedulerClient([])


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
    full_mock_scheduler_client: SchedulerClientInterface,
    mock_katalogus_client: KatalogusClientInterface,
    mock_octopoes_client: OctopoesClientInterface,
    mock_boefje_runner_client: BoefjeRunnerClientInterface,
) -> TestClient:
    from luik.server import app

    app.dependency_overrides[get_scheduler_client] = lambda: full_mock_scheduler_client
    app.dependency_overrides[get_katalogus_client] = lambda: mock_katalogus_client
    app.dependency_overrides[get_octopoes_client] = lambda: mock_octopoes_client
    app.dependency_overrides[get_boefje_runner_client] = (
        lambda: mock_boefje_runner_client
    )

    return TestClient(app)


@pytest.fixture
def authenticated_api(
    full_mock_scheduler_client: SchedulerClientInterface,
    mock_katalogus_client: KatalogusClientInterface,
    mock_octopoes_client: OctopoesClientInterface,
    mock_boefje_runner_client: BoefjeRunnerClientInterface,
) -> TestClient:
    from luik.server import app

    app.dependency_overrides[get_scheduler_client] = lambda: full_mock_scheduler_client
    app.dependency_overrides[get_katalogus_client] = lambda: mock_katalogus_client
    app.dependency_overrides[get_octopoes_client] = lambda: mock_octopoes_client
    app.dependency_overrides[get_boefje_runner_client] = (
        lambda: mock_boefje_runner_client
    )

    client = TestClient(app)
    client.headers.update({"luik-api-key": "super_secret_password"})

    return client
