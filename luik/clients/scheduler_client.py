import structlog
from httpx import Client, HTTPTransport
from pydantic import TypeAdapter

from luik.models.api_models import (
    Filter,
    PaginatedResponse,
    Queue,
    QueuePopRequest,
    Task,
    TaskStatus,
)
from luik.config import settings

logger = structlog.get_logger(__name__)

IMPLEMENTED_OOIS = {"IPAddressV4", "IPAddressV6"}


class SchedulerClientInterface:
    def get_queues(self) -> list[Queue]:
        raise NotImplementedError()

    def pop_task(
        self,
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
        task_capabilities: list[str] = [],
        reachable_networks: list[str] = [],
    ) -> Task | None:
        accepted_oois = IMPLEMENTED_OOIS.intersection(set(task_capabilities))

        response = self._session.get(
            "/tasks", params={"limit": "100", "task_type": "boefje", "status": "queued"}
        )

        if response.is_error:
            logger.error(
                "Error fetching queued tasks",
                status_code=response.status_code,
                text=response.text,
            )
            return None

        queued_tasks: PaginatedResponse[Task] = TypeAdapter(
            PaginatedResponse[Task]
        ).validate_json(response.content)

        logger.info("Queued tasks fetched", tasks=queued_tasks.model_dump_json())

        if queued_tasks.count == 0:
            logger.debug("No queued tasks available")
            return None

        found_task = None
        for task in queued_tasks.results:
            logger.info("Evaluating task", task_id=task.id)

            if (
                task.data.input_ooi.split("|")[0] in accepted_oois
                and task.data.input_ooi.split("|")[1] in reachable_networks
            ):
                logger.info("Task matched", task_id=task.id)
                found_task = task
                break

        if found_task is None:
            logger.info("No matching task found")
            return None

        response = self._session.post(
            "/schedulers/boefje/pop",
            content=QueuePopRequest(
                filters=[Filter(column="id", operator="==", value=found_task.id)]
            ).model_dump_json(),
            params={"limit": 1},
        )

        logger.info("Content of pop_task:\n%s", response.text)
        if response.is_error:
            return None

        dict_response = response.json()

        if len(dict_response["results"]) == 0:
            return None

        return TypeAdapter(Task | None).validate_python(dict_response["results"][0])

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
