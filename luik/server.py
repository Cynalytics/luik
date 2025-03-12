import multiprocessing
from multiprocessing.context import ForkContext, ForkProcess

from fastapi.security import OAuth2PasswordRequestForm
import structlog
from fastapi import Depends, FastAPI, Response, status
from uvicorn import Config, Server

from luik.api import router
from luik.auth import TokenResponse, get_access_token
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
def health() -> Response:
    return Response("OK", status_code=status.HTTP_200_OK)


@app.post("/token", response_model=TokenResponse)
def login(form_data: OAuth2PasswordRequestForm = Depends()) -> TokenResponse:
    access_token, expire_time = get_access_token(form_data)

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_at=expire_time.isoformat(),
    )
