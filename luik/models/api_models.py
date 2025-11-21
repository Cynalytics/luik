import datetime
from enum import Enum
from typing import Any, Generic, TypeVar

from pydantic import AwareDatetime, BaseModel

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    count: int
    next: str | None
    previous: str | None
    results: list[T]


class LuikPopRequest(BaseModel):
    """ "
    Request model for popping tasks with luikje.
        task_capabilities: list of OOIs that the kitten can handle. (This is also limited by the implemented ways of recognizing the network from input_ooi)
        reachable_networks: list of networks that the kitten can reach.
    """

    task_capabilities: list[str]
    reachable_networks: list[str]


class LuikPopResponse(BaseModel):
    oci_image: str
    task_id: str


class File(BaseModel):
    name: str | None = None
    content: str
    tags: list[str]


class Boefje(BaseModel):
    id: str
    version: Any = None


class ScanProfile(BaseModel):
    scan_profile_type: str
    reference: str
    level: int
    user_id: int


class Input(BaseModel):
    object_type: str
    scan_profile: ScanProfile
    user_id: int
    primary_key: str
    network: str
    address: str
    netblock: Any = None


class Arguments(BaseModel):
    oci_arguments: list[str]
    input: dict[
        str, Any
    ]  # This contains an OOI # TODO: import octopoes here. Ask how debian packages install octopoes


class BoefjeMeta(BaseModel):
    id: str
    started_at: AwareDatetime | None = None
    ended_at: AwareDatetime | None = None
    boefje: dict[str, Any]
    input_ooi: str
    arguments: Arguments | None = None
    organization: str
    runnable_hash: Any = None
    environment: dict[str, Any] = {}


class BoefjeInputResponse(BaseModel):
    output_url: str
    task: dict[str, Any]


class LuikBoefjeOutputRequest(BaseModel):
    status: str
    files: list[File]


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


class Task(BaseModel):
    id: str
    scheduler_id: str
    schedule_id: str | None = None
    priority: int
    status: TaskStatus
    type: str
    hash: str | None = None
    data: BoefjeMeta
    created_at: datetime.datetime
    modified_at: datetime.datetime


class Filter(BaseModel):
    column: str
    field: str | None = None
    operator: str
    value: Any


class QueuePopRequest(BaseModel):
    filters: list[Filter]


class BoefjeMetaRequest(BaseModel):
    task_data: BoefjeMeta
    oci_arguments: list[str]
