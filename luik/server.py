import multiprocessing
from multiprocessing.context import ForkContext, ForkProcess

import structlog
from fastapi import FastAPI
from uvicorn import Config, Server

from luik.api import router
from luik.config import settings


app = FastAPI(title="Luik API")
app.include_router(router)
logger = structlog.get_logger(__name__)
ctx: ForkContext = multiprocessing.get_context("fork")


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
def health() -> str:
    return "OK"
