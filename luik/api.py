from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status
import structlog

from luik.auth import authenticate_token
from luik.clients.boefje_runner_client import (
    BoefjeRunnerClientInterface,
    get_boefje_runner_client,
)
from luik.clients.katalogus_client import KatalogusClientInterface, get_katalogus_client
from luik.clients.scheduler_client import (
    SchedulerClientInterface,
    get_scheduler_client,
)
from luik.models.api_models import (
    LuikBoefjeOutputRequest,
    LuikPopRequest,
    LuikPopResponse,
    TaskStatus,
)


logger = structlog.get_logger(__name__)

router = APIRouter(dependencies=[Depends(authenticate_token)])


@router.post("/pop/{queue_id}", response_model=LuikPopResponse)
def pop_task(
    queue_id: str,
    request: LuikPopRequest,
    scheduler_client: SchedulerClientInterface = Depends(get_scheduler_client),
    katalogus_client: KatalogusClientInterface = Depends(get_katalogus_client),
) -> LuikPopResponse | Response:
    logger.info("Popping task for queue: %s", queue_id)
    logger.info("With request:\n%s", request.model_dump_json())
    task = scheduler_client.pop_task(
        queue_id, request.task_capabilities, request.reachable_networks
    )
    if task is None:
        logger.info("No task found for queue %s.", queue_id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    logger.info("Task:\n%s", task.model_dump_json())

    plugin = katalogus_client.get_boefje_plugin(task.data.boefje["id"])
    if plugin is None:
        logger.critical("Task found, but boefje does not exist for task. %s.", queue_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Task found, but boefje does not exist for task. {queue_id}.",
        )
    return LuikPopResponse(task_id=task.id, oci_image=plugin.oci_image)


@router.get("/boefje/input/{task_id}")
def boefje_input(
    task_id: UUID,
    scheduler_client: SchedulerClientInterface = Depends(get_scheduler_client),
    boefje_runner_client: BoefjeRunnerClientInterface = Depends(
        get_boefje_runner_client
    ),
) -> dict[str, Any]:
    scheduler_client.patch_task(str(task_id), TaskStatus.RUNNING)

    prepared_boefje_input = boefje_runner_client.boefje_input(str(task_id))
    if prepared_boefje_input is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Could not get boefje input from task: {task_id}.",
        )

    logger.info("Boefje input:\n%s", prepared_boefje_input)
    return prepared_boefje_input


@router.post("/boefje/output/{task_id}")
def boefje_output(
    task_id: str,
    boefje_output: LuikBoefjeOutputRequest,
    boefje_runner_client: BoefjeRunnerClientInterface = Depends(
        get_boefje_runner_client
    ),
) -> Any:
    try:
        boefje_runner_client.boefje_output(task_id, boefje_output)
    except HTTPException as e:
        return HTTPException(
            status_code=e.status_code,
            detail=f"Calling the boefje output went wrong.\n{e.detail}",
        )

    return Response(status_code=status.HTTP_200_OK)
