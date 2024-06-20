from cloudwash.config import settings
from cloudwash.entities.resources.base import NicsCleanup
from cloudwash.logger import logger
from cloudwash.utils import dry_data


class CleanNics(NicsCleanup):
    def __init__(self, client):
        self.client = client
        self._delete = []
        self.list()

    def _set_dry(self):
        dry_data['NICS']['delete'] = self._delete

    def list(self):
        pass

    def remove(self):
        pass

    def cleanup(self):
        if not settings.dry_run:
            self.remove()


class CleanAWSNics(CleanNics):
    def list(self):
        if settings.aws.criteria.nic.unassigned:
            rnics = self.client.get_all_unused_network_interfaces()
            rnics = [rnic["NetworkInterfaceId"] for rnic in rnics]
            self._delete.extend(rnics)
        self._set_dry()

    def remove(self):
        self.client.remove_all_unused_nics()
        logger.info(f"Removed Nics: \n{self._delete}")


class CleanAzureNics(CleanNics):
    def list(self):
        if settings.azure.criteria.nic.unassigned:
            rnics = self.client.list_free_nics()
            self._delete.extend(rnics)
        self._set_dry()

    def remove(self):
        self.client.remove_nics_by_search()
        logger.info(f"Removed Nics: \n{self._delete}")
