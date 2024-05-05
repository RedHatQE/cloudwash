from cloudwash.entities.resources.discs import CleanAWSDiscs
from cloudwash.entities.resources.discs import CleanAzureDiscs
from cloudwash.entities.resources.images import CleanAWSImages
from cloudwash.entities.resources.images import CleanAzureImages
from cloudwash.entities.resources.nics import CleanAWSNics
from cloudwash.entities.resources.nics import CleanAzureNics
from cloudwash.entities.resources.pips import CleanAWSPips
from cloudwash.entities.resources.pips import CleanAzurePips
from cloudwash.entities.resources.stacks import CleanAWSStacks
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

    @property
    def nics(self):
        providerclass = self.__class__.__name__
        if 'Azure' in providerclass:
            return CleanAzureNics(client=self.client)
        elif 'AWS' in providerclass:
            return CleanAWSNics(client=self.client)

    @property
    def pips(self):
        providerclass = self.__class__.__name__
        if 'Azure' in providerclass:
            return CleanAzurePips(client=self.client)
        elif 'AWS' in providerclass:
            return CleanAWSPips(client=self.client)

    @property
    def images(self):
        providerclass = self.__class__.__name__
        if 'Azure' in providerclass:
            return CleanAzureImages(client=self.client)
        elif 'AWS' in providerclass:
            return CleanAWSImages(client=self.client)

    @property
    def stacks(self):
        providerclass = self.__class__.__name__
        if 'AWS' in providerclass:
            return CleanAWSStacks(client=self.client)


class AzureCleanup(providerCleanup):
    def __init__(self, client):
        self.client = client
        super().__init__(client)


class AWSCleanup(providerCleanup):
    def __init__(self, client):
        self.client = client
        super().__init__(client)
