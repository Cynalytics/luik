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
PASSWORD = "ac36e8d26bd00b068bf0c3558eac748402d14f469f908eb7ff92b0ead9700dda"  # "super_secret_password" hashed


@pytest.fixture(scope="session", autouse=True)
def set_env() -> None:
    os.environ["OCTOPOES_API"] = PLACEHOLDER_URL
    os.environ["KATALOGUS_API"] = PLACEHOLDER_URL
    os.environ["SCHEDULER_API"] = PLACEHOLDER_URL
    os.environ["BOEFJE_RUNNER_API"] = PLACEHOLDER_URL

    os.environ["KATALOGUS_DB_URI"] = (
        f"postgresql://katalogus_db:foo@{PLACEHOLDER_URL}/katalogus"
    )
    os.environ["TOKEN_SECRET"] = PASSWORD

    os.environ["API"] = PLACEHOLDER_URL


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
    client.headers.update({"luik-api-key": "super_secret_password"})

    return client
