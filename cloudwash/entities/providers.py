from cloudwash.entities.resources.discs import CleanAWSDiscs
from cloudwash.entities.resources.discs import CleanAzureDiscs
from cloudwash.entities.resources.vms import CleanAWSVms
from cloudwash.entities.resources.vms import CleanAzureVMs


class providerCleanup:
    def __init__(self, client):
        self.client = client

    @property
    def vms(self):
        providerclass = self.__class__.__name__
        if 'Azure' in providerclass:
            return CleanAzureVMs(client=self.client)
        elif 'AWS' in providerclass:
            return CleanAWSVms(client=self.client)

    @property
    def discs(self):
        providerclass = self.__class__.__name__
        if 'Azure' in providerclass:
            return CleanAzureDiscs(client=self.client)
        elif 'AWS' in providerclass:
            return CleanAWSDiscs(client=self.client)


class AzureCleanup(providerCleanup):
    def __init__(self, client):
        self.client = client
        super().__init__(client)


class AWSCleanup(providerCleanup):
    def __init__(self, client):
        self.client = client
        super().__init__(client)
