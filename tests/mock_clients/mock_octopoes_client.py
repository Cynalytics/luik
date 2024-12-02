from datetime import datetime
from typing import Any
from luik.clients.octopoes_client import OctopoesClientInterface


class MockOctopoesClient(OctopoesClientInterface):
    def get_ooi_by_reference(
        self, org_code: str, reference: str, valid_time: datetime
    ) -> dict[str, Any]:
        raise NotImplementedError()
