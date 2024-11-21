import multiprocessing
from multiprocessing.context import ForkContext, ForkProcess

import structlog
from fastapi import Depends, FastAPI
from uvicorn import Config, Server

from luik.clients.bytes_client import BytesAPIClient
from luik.clients.katalogus_client import KatalogusClient, get_katalogus_client
from luik.clients.scheduler_client import SchedulerAPIClient, SchedulerClientInterface
from luik.config import settings
from luik.models.api_models import LuikPopRequest, LuikPopResponse

app = FastAPI(title="Boefje API")
logger = structlog.get_logger(__name__)
ctx: ForkContext = multiprocessing.get_context("fork")


def get_scheduler_client():
    return SchedulerAPIClient(str(settings.scheduler_api))


def get_bytes_client():
    return BytesAPIClient(str(settings.scheduler_api))


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


@app.post("/pop/{queue_id}")
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

    plugin = katalogus_client.getPlugin(task.data.boefje["id"])
    if task is None:
        logger.error("Task found, but boefje does not exist for task. %s.", queue_id)
        return None
    return LuikPopResponse(task_id=task.id, oci_image=plugin.oci_image)
