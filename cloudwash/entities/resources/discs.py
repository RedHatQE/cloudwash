from cloudwash.config import settings
from cloudwash.entities.resources.base import DiscsCleanup
from cloudwash.logger import logger
from cloudwash.utils import dry_data


class CleanDiscs(DiscsCleanup):
    def __init__(self, client):
        self.client = client
        self._delete = []
        self.list()

    def _set_dry(self):
        # VMsContainer = namedtuple('VMsCotainer', ['delete', 'stop', 'skip'])
        # return VMsContainer(self._delete, self._stop, self._skip)
        dry_data['DISCS']['delete'] = self._delete

    def list(self):
        pass

    def remove(self):
        pass

    def cleanup(self):
        if not settings.dry_run:
            self.remove()


class CleanAWSDiscs(CleanDiscs):
    def list(self):
        if settings.aws.criteria.disc.unassigned:
            rdiscs = self.client.get_all_unattached_volumes()
            rdiscs = [rdisc["VolumeId"] for rdisc in rdiscs]
            self._delete.extend(rdiscs)
        self._set_dry()

    def remove(self):
        self.client.remove_all_unused_volumes()
        logger.info(f"Removed Discs: \n{self._delete}")


class CleanAzureDiscs(CleanDiscs):
    def list(self):
        if settings.azure.criteria.disc.unassigned:
            rdiscs = self.client.list_free_discs()
            self._delete.extend(rdiscs)
        self._set_dry()

    def remove(self):
        self.client.remove_discs_by_search()
        logger.info(f"Removed Discs: \n{self._delete}")
