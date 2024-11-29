from pydantic import BaseModel


class KatalogusBoefje(BaseModel):
    plugin_id: str
    name: str
    scan_level: int
    consumes: list[str]
    produces: list[str]
    oci_image: str
    oci_arguments: list[str]
