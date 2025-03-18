import os
from pathlib import Path

from pydantic import AnyHttpUrl, Field, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict
import structlog

BASE_DIR: Path = Path(__file__).parent.resolve()

# Set base dir to something generic when compiling environment docs
if os.getenv("DOCS"):
    BASE_DIR = Path("../")


class Settings(BaseSettings):
    katalogus_db_uri: PostgresDsn = Field(
        examples=["postgresql://xx:xx@host:5432/katalogus"],
        description="Katalogus Postgres DB URI",
    )

    scheduler_api: AnyHttpUrl = Field(
        examples=["http://localhost:8004"], description="Mula API URL"
    )
    katalogus_api: AnyHttpUrl = Field(
        examples=["http://localhost:8003"], description="Katalogus API URL"
    )
    octopoes_api: AnyHttpUrl = Field(
        examples=["http://localhost:8001"], description="Octopoes API URL"
    )
    boefje_runner_api: AnyHttpUrl = Field()

    api: AnyHttpUrl = Field(AnyHttpUrl("http://localhost:8019"))

    response_host: AnyHttpUrl = Field(AnyHttpUrl("http://localhost:8007"))

    auth_password: str = Field(
        examples=["password"], description="Password for authentication"
    )

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def api_host(self) -> str:
        if not self.api.host:
            raise Exception("Api does not have a host")
        return self.api.host

    @property
    def api_port(self) -> int:
        if not self.api.port:
            raise Exception("Api does not have a port")
        return self.api.port


settings = Settings()


if __name__ == "__main__":
    logger = structlog.get_logger(__name__)
    logger.info(settings.model_dump_json())
