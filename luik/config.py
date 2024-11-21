import os
from pathlib import Path
from typing import Literal

from pydantic import AmqpDsn, AnyHttpUrl, Field, FilePath, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR: Path = Path(__file__).parent.resolve()

# Set base dir to something generic when compiling environment docs
if os.getenv("DOCS"):
    BASE_DIR = Path("../")


class Settings(BaseSettings):
    log_cfg: FilePath = Field(
        BASE_DIR / "logging.json", description="Path to the logging configuration file"
    )

    # Worker configuration
    pool_size: int = Field(2, description="Number of workers to run per queue")
    poll_interval: float = Field(
        10.0,
        description="Time to wait before polling for tasks when all queues are empty",
    )
    worker_heartbeat: float = Field(
        1.0,
        description="Seconds to wait before checking the workers when queues are full",
    )

    # Queue configuration
    queue_uri: AmqpDsn = Field(
        ...,
        description="KAT queue URI",
        examples=["amqp://"],
        validation_alias="QUEUE_URI",
    )

    katalogus_db_uri: PostgresDsn = Field(
        ...,
        examples=["postgresql://xx:xx@host:5432/katalogus"],
        description="Katalogus Postgres DB URI",
        validation_alias="KATALOGUS_DB_URI",
    )

    scheduler_api: AnyHttpUrl = Field(
        ...,
        examples=["http://localhost:8004"],
        description="Mula API URL",
        validation_alias="SCHEDULER_API",
    )
    katalogus_api: AnyHttpUrl = Field(
        ...,
        examples=["http://localhost:8003"],
        description="Katalogus API URL",
        validation_alias="KATALOGUS_API",
    )
    octopoes_api: AnyHttpUrl = Field(
        ...,
        examples=["http://localhost:8001"],
        description="Octopoes API URL",
        validation_alias="OCTOPOES_API",
    )
    api: AnyHttpUrl = Field(
        ...,
        examples=["http://boefje:8000"],
        description="The URL on which the boefjes API is available",
    )
    # Boefje server settings
    api_host: str = Field(
        "0.0.0.0", description="Host address of the Boefje API server"
    )
    api_port: int = Field(8000, description="Host port of the Boefje API server")
    bytes_api: AnyHttpUrl = Field(
        ...,
        examples=["http://localhost:8002"],
        description="Bytes API URL",
        validation_alias="BYTES_API",
    )
    bytes_username: str = Field(
        ...,
        examples=["test"],
        description="Bytes JWT login username",
        validation_alias="BYTES_USERNAME",
    )
    bytes_password: str = Field(
        ...,
        examples=["secret"],
        description="Bytes JWT login password",
        validation_alias="BYTES_PASSWORD",
    )

    logging_format: Literal["text", "json"] = Field(
        "text", description="Logging format"
    )

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")



settings = Settings()
