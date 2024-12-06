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

    api_host: str = Field(
        "localhost", description="Host address of the Boefje API server"
    )
    api_port: int = Field(8019, description="Host port of the Boefje API server")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()


if __name__ == "__main__":
    logger = structlog.get_logger(__name__)
    logger.info(settings.model_dump_json())
