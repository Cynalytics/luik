import datetime
import json
import logging
import uuid
from base64 import b64encode
from collections.abc import Set
from enum import Enum
from typing import Any

from httpx import Client, HTTPTransport, Response
from pydantic import AwareDatetime, BaseModel, Field, TypeAdapter


class Queue(BaseModel):
    id: str
    size: int


class TaskStatus(Enum):
    """Status of a task."""

    PENDING = "pending"
    QUEUED = "queued"
    DISPATCHED = "dispatched"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class BoefjeMeta(BaseModel):
    id: str
    boefje: dict[str, Any]
    input_ooi: str | None = None
    arguments: dict = {}
    organization: str
    runnable_hash: str | None = None
    environment: dict[str, str] = {}

    started_at: AwareDatetime | None = Field(default=None)
    ended_at: AwareDatetime | None = Field(default=None)


class Task(BaseModel):
    id: uuid.UUID
    scheduler_id: str
    schedule_id: str | None
    priority: int
    status: TaskStatus
    type: str
    hash: str | None = None
    data: BoefjeMeta
    created_at: datetime.datetime
    modified_at: datetime.datetime


class Filter(BaseModel):
    column: str
    field: str
    operator: str
    value: Any


class QueuePopRequest(BaseModel):
    filters: list[Filter]


class BoefjeMetaRequest(BaseModel):
    task_data: BoefjeMeta
    oci_arguments: list[str]


class BytesClientInterface:
    def get_queues(self) -> list[Queue]:
        raise NotImplementedError()

    def pop_task(self, queue_id: str) -> Task | None:
        raise NotImplementedError()

    def patch_task(self, task_id: uuid.UUID, status: TaskStatus) -> None:
        raise NotImplementedError()

    def get_task(self, task_id: uuid.UUID) -> Task:
        raise NotImplementedError()


class BytesAPIClient(BytesClientInterface):
    def __init__(self, base_url: str):
        self._session = Client(base_url=base_url, transport=HTTPTransport(retries=6))

    def pop_task(
        self, queue_id: str, task_capabilities: list[str] = [], reachable_networks: list[str] = []
    ) -> Task | None:
        filters: list[Filter] = []

        # Client should only pop tasks that lie on a network that the runner is capable of reaching (e.g. the internet)
        if reachable_networks:
            filters.append(Filter(column="data", field="network", operator="<@", value=json.dumps(reachable_networks)))

        # Client should only pop tasks that have requirements that this runner is capable of (e.g. being able
        # to handle ipv6 requests)
        if task_capabilities:
            filters.append(
                Filter(column="data", field="requirements", operator="<@", value=json.dumps(task_capabilities))
            )

        response = self._session.post(
            f"/queues/{queue_id}/pop", data=QueuePopRequest(filters=filters).model_dump_json()
        )
        response.raise_for_status()

        return TypeAdapter(Task | None).validate_json(response.content)

    def patch_task(self, task_id: uuid.UUID, status: TaskStatus) -> None:
        response = self._session.patch(f"/tasks/{task_id}", json={"status": status.value})
        response.raise_for_status()

    def get_task(self, task_id: uuid.UUID) -> Task:
        response = self._session.get(f"/tasks/{task_id}")
        response.raise_for_status()

        return Task.model_validate_json(response.content)
