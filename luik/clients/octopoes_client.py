from datetime import datetime
from typing import Any

import structlog
from httpx import Client, HTTPTransport
from pydantic import TypeAdapter

logger = structlog.get_logger(__name__)


class OctopoesClient:
    def __init__(self, base_url: str):
        self._session = Client(base_url=base_url, transport=HTTPTransport(retries=6))

    def get(self, org_code: str, reference: str, valid_time: datetime) -> dict[str, Any]:
        res = self._session.get(
            f"/{org_code}/object", params={"reference": str(reference), "valid_time": str(valid_time)}
        )
        return TypeAdapter(dict[str, Any]).validate_json(res.content)
