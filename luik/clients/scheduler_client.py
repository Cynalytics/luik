import json

import structlog
from httpx import Client, HTTPTransport
from pydantic import TypeAdapter

from luik.models.api_models import Filter, Queue, QueuePopRequest, Task, TaskStatus
from luik.config import settings

logger = structlog.get_logger(__name__)


class SchedulerClientInterface:
    def get_queues(self) -> list[Queue]:
        raise NotImplementedError()

    def pop_task(
        self,
        queue_id: str,
        task_capabilities: list[str] = [],
        reachable_networks: list[str] = [],
    ) -> Task | None:
        raise NotImplementedError()

    def patch_task(self, task_id: str, status: TaskStatus) -> None:
        raise NotImplementedError()

    def get_task(self, task_id: str) -> Task:
        raise NotImplementedError()


class SchedulerClient(SchedulerClientInterface):
    def __init__(self, base_url: str):
        self._session = Client(base_url=base_url, transport=HTTPTransport(retries=6))

    def pop_task(
        self,
        queue_id: str,
        task_capabilities: list[str] = [],
        reachable_networks: list[str] = [],
    ) -> Task | None:
        filters: list[Filter] = []

        # Client should only pop tasks that lie on a network that the runner is capable of reaching (e.g. the internet)
        if reachable_networks:
            filters.append(
                Filter(
                    column="data",
                    field="network",
                    operator="<@",
                    value=json.dumps(reachable_networks),
                )
            )

        # Client should only pop tasks that have requirements that this runner is capable of (e.g. being able
        # to handle ipv6 requests)
        if task_capabilities:
            filters.append(
                Filter(
                    column="data",
                    field="requirements",
                    operator="<@",
                    value=json.dumps(task_capabilities),
                )
            )

        response = self._session.post(
            f"/queues/{queue_id}/pop",
            content=QueuePopRequest(filters=filters).model_dump_json(),
        )

        # TODO: Currently openkat returns an error (404) when no task is found. This needs better handling

        logger.info("Content of pop_task:\n%s", response.text)
        if response.is_error:
            return None
        return TypeAdapter(Task | None).validate_json(response.content)

    def patch_task(self, task_id: str, status: TaskStatus) -> None:
        response = self._session.patch(
            f"/tasks/{task_id}", json={"status": status.value}
        )
        response.raise_for_status()

    def get_task(self, task_id: str) -> Task:
        response = self._session.get(f"/tasks/{task_id}")
        response.raise_for_status()

        return Task.model_validate_json(response.content)


def get_scheduler_client() -> SchedulerClientInterface:
    return SchedulerClient(str(settings.scheduler_api))
