import multiprocessing
from multiprocessing.context import ForkContext, ForkProcess
from typing import Any

import structlog
from fastapi import Depends, FastAPI, HTTPException, Response, status
from uvicorn import Config, Server

from luik.clients.boefje_runner_client import (
    BoefjeRunnerClient,
    BoefjeRunnerClientInterface,
)
from luik.clients.katalogus_client import KatalogusClient, KatalogusClientInterface
from luik.clients.octopoes_client import OctopoesClient, OctopoesClientInterface
from luik.clients.scheduler_client import (
    SchedulerClient,
    SchedulerClientInterface,
)
from luik.config import settings
from luik.models.api_models import (
    LuikBoefjeOutputRequest,
    LuikPopRequest,
    LuikPopResponse,
    TaskStatus,
)

app = FastAPI(title="Luik API")
logger = structlog.get_logger(__name__)
ctx: ForkContext = multiprocessing.get_context("fork")


def get_scheduler_client() -> SchedulerClientInterface:
    return SchedulerClient(str(settings.scheduler_api))


def get_katalogus_client() -> KatalogusClientInterface:
    return KatalogusClient(str(settings.katalogus_db_uri))


def get_octopoes_client() -> OctopoesClientInterface:
    return OctopoesClient(str(settings.octopoes_api))


def get_boefje_runner_client() -> BoefjeRunnerClientInterface:
    return BoefjeRunnerClient(str(settings.boefje_runner_api))


class UvicornServer(ForkProcess):
    def __init__(self, config: Config):
        super().__init__()
        self.server = Server(config=config)
        self.config = config

    def stop(self) -> None:
        self.terminate()

    def run(self) -> None:
        self.server.run()


def run() -> UvicornServer:
    config = Config(app, host=settings.api_host, port=settings.api_port)
    instance = UvicornServer(config=config)
    instance.start()
    return instance


@app.get("/health")
def health() -> Response:
    return Response("OK", status_code=status.HTTP_200_OK)


@app.post("/pop/{queue_id}", response_model=LuikPopResponse)
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


@app.get("/boefje/input/{task_id}")
def boefje_input(
    task_id: str,
    scheduler_client: SchedulerClientInterface = Depends(get_scheduler_client),
    boefje_runner_client: BoefjeRunnerClientInterface = Depends(
        get_boefje_runner_client
    ),
) -> dict[str, Any]:
    scheduler_client.patch_task(task_id, TaskStatus.RUNNING)

    prepared_boefje_input = boefje_runner_client.boefje_input(task_id)
    if prepared_boefje_input is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Could not get boefje input from task: {task_id}.",
        )

    prepared_boefje_input["output_url"] = (
        str(settings.api).rstrip("/")
        + f"/boefje/output/{task_id}"  # TODO: is this the correct way of giving the url?
    )

    return prepared_boefje_input


@app.post("/boefje/output/{task_id}")
def boefje_output(
    task_id: str,
    boefje_output: LuikBoefjeOutputRequest,
    boefje_runner_client: BoefjeRunnerClientInterface = Depends(
        get_boefje_runner_client
    ),
) -> Any:
    logger.info("Boefje output with:")
    logger.info(task_id)
    logger.info(boefje_output.model_dump_json())
    try:
        boefje_runner_client.boefje_output(task_id, boefje_output)
    except HTTPException as e:
        return HTTPException(
            status_code=e.status_code,
            detail=f"Calling the boefje output went wrong.\n{e.detail}",
        )

    return Response(status_code=status.HTTP_200_OK)
