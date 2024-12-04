from luik.clients.katalogus_client import KatalogusClientInterface
from luik.models.db_models import KatalogusBoefje


class MockKatalogusClient(KatalogusClientInterface):
    def get_boefje_plugin(self, plugin_id: str) -> KatalogusBoefje | None:
        if plugin_id == "non_existent":
            return None
        return KatalogusBoefje(
            plugin_id=plugin_id,
            name="name",
            scan_level=1,
            consumes=["consumption"],
            produces=["product"],
            oci_image=f"oci/{plugin_id}",
            oci_arguments=[],
        )
