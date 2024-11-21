from pydantic import BaseModel, Field


class LuikPopRequest(BaseModel):
    task_capabilities: list[str] = Field([])
    reachable_networks: list[str] = Field([])


class LuikPopResponse(BaseModel):
    oci_image: str
    task_id: str
