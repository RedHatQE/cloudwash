from cloudwash.entities.resources.vms import CleanVMs


class providerCleanup:
    def __init__(self, client):
        self.client = client

    @property
    def vms(self):
        return CleanVMs(client=self.client)
