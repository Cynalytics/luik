import os
from pathlib import Path

from pydantic import AnyHttpUrl, Field, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict
import structlog

BASE_DIR: Path = Path(__file__).parent.resolve()

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

    token_secret: str = Field(
        examples=["2bb80d537b1da3e38bd30361aa855686bde0eacd7162fef6a25fe97bf527a25b"],
        description="Secret for token generation",
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
