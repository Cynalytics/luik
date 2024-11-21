import json
import uuid
from base64 import b64encode
from collections.abc import Set
from datetime import datetime, timezone
from enum import Enum
from typing import Any

import structlog
from httpx import Client, HTTPTransport, Response
from pydantic import AwareDatetime, BaseModel, Field, TypeAdapter

from luik.config import settings

logger = structlog.get_logger(__name__)


def get_octopoes_client():
    return OctopoesClient(str(settings.octopoes_api))


class OctopoesClient:
    def __init__(self, base_url: str):
        self._session = Client(base_url=base_url, transport=HTTPTransport(retries=6))

    def get(self, org_code: str, reference: str, valid_time: datetime) -> dict[str, Any]:
        res = self._session.get(
            f"/{org_code}/object", params={"reference": str(reference), "valid_time": str(valid_time)}
        )
        return TypeAdapter(dict[str, Any]).validate_json(res.content)


OC = get_octopoes_client()

x = OC.get("cyn", "IPAddressV4|internet|46.23.85.171", datetime.now(timezone.utc))
logger.info(x)
logger.info(type(x))
