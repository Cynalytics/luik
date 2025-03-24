import datetime
from typing import Any

from fastapi import HTTPException
from luik.clients.scheduler_client import SchedulerClientInterface
from luik.models.api_models import Arguments, BoefjeMeta, Queue, Task, TaskStatus
import structlog

logger = structlog.get_logger(__name__)


class MockSchedulerClient(SchedulerClientInterface):
    def __init__(self, queue: list[dict[str, Any]]):
        self.queue = queue

    def get_queues(self) -> list[Queue]:
        raise NotImplementedError()

    def pop_task(
        self,
        task_capabilities: list[str] = [],
        reachable_networks: list[str] = [],
    ) -> Task | None:
        if not (task_capabilities and reachable_networks):
            raise Exception(f"Empty value given to {self.pop_task.__name__}")
        if len(self.queue) == 0:
            return None
        return Task.model_validate(self.queue.pop())

    def patch_task(self, task_id: str, status: TaskStatus) -> None:
        for task in self.queue:
            if task["id"] == task_id:
                task["status"] = status.value
                return

        raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")

    def get_task(self, task_id: str) -> Task:
        raise NotImplementedError()


class SimpleMockSchedulerClient(SchedulerClientInterface):
    def pop_task(
        self,
        queue_id: str,
        task_capabilities: list[str] = [],
        reachable_networks: list[str] = [],
    ) -> Task:
        boefje_meta = BoefjeMeta(
            id="meta123",
            boefje={"id": "nmap", "name": "Nmap TCP", "version": "1.0"},
            input_ooi="IPAddressV4|internet|46.23.85.171",
            organization="cyn",
            arguments=Arguments(
                oci_arguments=["--scan", "--fast"], input={"network": "internet"}
            ),
        )

        task = Task(
            id="task123",
            scheduler_id="boefje-scheduler",
            priority=1,
            status=TaskStatus.PENDING,
            type="boefje",
            hash="abcdef123456",
            data=boefje_meta,
            created_at=datetime.datetime.utcnow(),
            modified_at=datetime.datetime.utcnow(),
        )

        return task
