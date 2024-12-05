from cloudwash.config import settings
from cloudwash.entities.resources.base import PipsCleanup
from cloudwash.logger import logger
from cloudwash.utils import dry_data


class CleanPips(PipsCleanup):
    def __init__(self, client):
        self.client = client
        self._delete = []
        self.list()

    def _set_dry(self):
        dry_data['PIPS']['delete'] = self._delete

    def list(self):
        pass

    def remove(self):
        pass

    def cleanup(self):
        if not settings.dry_run:
            self.remove()


class CleanAWSPips(CleanPips):
    def list(self):
        if settings.aws.criteria.public_ip.unassigned:
            dpips = self.client.get_all_disassociated_addresses()
            dpips = [dpip["AllocationId"] for dpip in dpips]
            self._delete.extend(dpips)
        self._set_dry()

    def remove(self):
        self.client.remove_all_unused_ips()
        logger.info(f"Removed Pips: \n{self._delete}")


class CleanAzurePips(CleanPips):
    def list(self):
        if settings.azure.criteria.public_ip.unassigned:
            dpips = self.client.list_free_pip()
            self._delete.extend(dpips)
        self._set_dry()

    def remove(self):
        self.client.remove_pips_by_search()
        logger.info(f"Removed Pips: \n{self._delete}")
