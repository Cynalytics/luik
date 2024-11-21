import multiprocessing
from datetime import datetime, timezone
from multiprocessing.context import ForkContext, ForkProcess

import structlog
from fastapi import Depends, FastAPI, HTTPException, status
from uvicorn import Config, Server

from luik.clients.boefje_runner_client import BoefjeRunnerClient
from luik.clients.bytes_client import BytesAPIClient
from luik.clients.katalogus_client import KatalogusClient
from luik.clients.octopoes_client import OctopoesClient
from luik.clients.scheduler_client import SchedulerAPIClient, SchedulerClientInterface, TaskStatus
from luik.config import settings
from luik.models.api_models import (
    Arguments,
    Boefje,
    BoefjeMeta,
    Input,
    LuikBoefjeInputResponse,
    LuikPopRequest,
    LuikPopResponse,
)

app = FastAPI(title="Boefje API")
logger = structlog.get_logger(__name__)
ctx: ForkContext = multiprocessing.get_context("fork")


def get_scheduler_client():
    return SchedulerAPIClient(str(settings.scheduler_api))


def get_katalogus_client():
    return KatalogusClient(str(settings.katalogus_db_uri))


def get_bytes_client():
    return BytesAPIClient(str(settings.scheduler_api))


def get_octopoes_client():
    return OctopoesClient(str(settings.octopoes_api))


def get_boefje_runner_client():
    return BoefjeRunnerClient(str(settings.boefje_runner_api))


class UvicornServer(ForkProcess):
    def __init__(self, config: Config):
        super().__init__()
        self.server = Server(config=config)
        self.config = config

    def stop(self):
        self.terminate()

    def run(self, *args, **kwargs):
        self.server.run()


def run():
    config = Config(app, host=settings.api_host, port=settings.api_port)
    instance = UvicornServer(config=config)
    instance.start()
    return instance


@app.post("/pop/{queue_id}", response_model=LuikPopResponse)
def pop_task(
    queue_id: str,
    request: LuikPopRequest,
    scheduler_client: SchedulerClientInterface = Depends(get_scheduler_client),
    katalogus_client: KatalogusClient = Depends(get_katalogus_client),
):
    logger.info("Popping task for queue: %s", queue_id)
    logger.info("With request:\n%s", request.model_dump_json())
    task = scheduler_client.pop_task(queue_id, request.task_capabilities, request.reachable_networks)

    if task is None:
        logger.info("No task found for queue %s.", queue_id)
        return None

    logger.info("Task:\n%s", task.model_dump_json())

    plugin = katalogus_client.get_boefje_plugin(task.data.boefje["id"])
    if plugin is None:
        logger.error("Task found, but boefje does not exist for task. %s.", queue_id)
        return None
    return LuikPopResponse(task_id=task.id, oci_image=plugin.oci_image)


@app.get("/boefje/input/{task_id}")  # response_model=LuikBoefjeInputResponse)
def boefje_input(task_id: str, boefje_runner_client: BoefjeRunnerClient = Depends(get_boefje_runner_client)):
    result = boefje_runner_client.boefje_input(task_id)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Could not get boefje input from task: {task_id}."
        )
    return result
