from cloudwash.config import settings
from cloudwash.entities.resources.base import ContainerCleanup
from cloudwash.logger import logger
from cloudwash.utils import dry_data
from cloudwash.utils import total_running_time


class CleanContainers(ContainerCleanup):
    def __init__(self, client):
        self.client = client
        self._delete = []
        self._stop = []
        self._skip = []
        self.list()

    def _set_dry(self):
        dry_data['CONTAINERS']['delete'] = self._delete
        dry_data['CONTAINERS']['stop'] = self._stop
        dry_data['CONTAINERS']['skip'] = self._skip

    def list(self):
        pass

    def stop(self):
        for container in self._stop:
            self.client.get_container(key=container).stop()
        logger.info(f"Stopped Podman Containers: \n{self._stop}")

    def remove(self):
        for container in self._delete:
            self.client.get_container(key=container).delete(force=True)
        logger.info(f"Removed Podman Containers: \n{self._delete}")

    def skip(self):
        logger.info(f"Skipped VMs: \n{self._skip}")

    def cleanup(self):
        if not settings.dry_run:
            self.remove()
            self.stop()
            self.skip()


class CleanPodmanContainers(CleanContainers):
    def list(self):
        for container in self.client.containers:
            if container.name in settings.podman.exceptions.container.skip_list:
                self._skip.append(container.name)
                continue
            elif total_running_time(container).minutes >= settings.podman.criteria.container.sla:
                if container.name in settings.podman.exceptions.container.stop_list:
                    self._stop.append(container.name)
                    continue

                elif container.name.startswith(settings.podman.criteria.container.name_prefix):
                    self._delete.append(container.name)

        self._set_dry()
