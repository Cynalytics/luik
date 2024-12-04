from tests.mock_clients.mock_katalogus_client import MockKatalogusClient


def test_mock_katalogus_client(mock_katalogus_client: MockKatalogusClient):
    assert mock_katalogus_client.get_boefje_plugin("plugin-id")
    assert not mock_katalogus_client.get_boefje_plugin("non_existent")
