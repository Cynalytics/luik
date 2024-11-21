import structlog
from pydantic import BaseModel
from sqlalchemy import MetaData, Table, and_, create_engine, select

from luik.config import settings

logger = structlog.get_logger(__name__)


def get_katalogus_client():
    return KatalogusClient()


class KatalogusBoefje(BaseModel):
    plugin_id: str
    name: str
    scan_level: int
    consumes: list[str]
    produces: list[str]
    oci_image: str
    oci_arguments: list[str]


class KatalogusClient:
    def __init__(self):
        self._engine = create_engine(str(settings.katalogus_db_uri))

    def getPlugin(self, plugin_id: str):
        with self._engine.connect() as conn:
            metadata = MetaData()
            metadata.reflect(bind=self._engine)

            boefje_table = Table("boefje", metadata, autoload_with=self._engine)

            query = select(
                boefje_table.c.plugin_id,
                boefje_table.c.name,
                boefje_table.c.scan_level,
                boefje_table.c.consumes,
                boefje_table.c.produces,
                boefje_table.c.oci_image,
                boefje_table.c.oci_arguments,
            ).where(boefje_table.columns.plugin_id == plugin_id)
            logger.info(query)

            exe = conn.execute(query)  # executing the query
            result = exe.fetchone()  # extracting top 5 results
            logger.info("FOUND RESULT")
            if not result:
                return None

            return KatalogusBoefje(
                plugin_id=result[0],
                name=result[1],
                scan_level=result[2],
                consumes=result[3],
                produces=result[4],
                oci_image=result[5],
                oci_arguments=result[6],
            )