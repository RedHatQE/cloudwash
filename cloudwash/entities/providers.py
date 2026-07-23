from cloudwash.entities.resources.containers import CleanPodmanContainers
from cloudwash.entities.resources.discs import CleanAWSDiscs
from cloudwash.entities.resources.discs import CleanAzureDiscs
from cloudwash.entities.resources.images import CleanAWSImages
from cloudwash.entities.resources.images import CleanAzureImages
from cloudwash.entities.resources.nics import CleanAWSNics
from cloudwash.entities.resources.nics import CleanAzureNics
from cloudwash.entities.resources.ocps import CleanAWSOcps
from cloudwash.entities.resources.pips import CleanAWSPips
from cloudwash.entities.resources.pips import CleanAzurePips
from cloudwash.entities.resources.stacks import CleanAWSStacks
from cloudwash.entities.resources.vms import CleanAWSVms
from cloudwash.entities.resources.vms import CleanAzureVMs
from cloudwash.entities.resources.vms import CleanGCEVMs
from cloudwash.entities.resources.vms import CleanVMWareVMs
from cloudwash.utils import DryData


class providerCleanup:
    def __init__(self, client, dry_data=None):
        self.client = client
        self.dry_data = dry_data or DryData()

    @property
    def ocps(self):
        providerclass = self.__class__.__name__
        if 'AWS' in providerclass:
            return CleanAWSOcps(client=self.client, dry_data=self.dry_data)
        else:
            raise NotImplementedError(f'The OCPs cleanup on {providerclass} is not implemented')

    @property
    def vms(self):
        providerclass = self.__class__.__name__
        if 'Azure' in providerclass:
            return CleanAzureVMs(client=self.client, dry_data=self.dry_data)
        elif 'AWS' in providerclass:
            return CleanAWSVms(client=self.client, dry_data=self.dry_data)
        elif 'GCE' in providerclass:
            return CleanGCEVMs(client=self.client, dry_data=self.dry_data)
        elif 'VMWare' in providerclass:
            return CleanVMWareVMs(client=self.client, dry_data=self.dry_data)

    @property
    def discs(self):
        providerclass = self.__class__.__name__
        if 'Azure' in providerclass:
            return CleanAzureDiscs(client=self.client, dry_data=self.dry_data)
        elif 'AWS' in providerclass:
            return CleanAWSDiscs(client=self.client, dry_data=self.dry_data)

    @property
    def nics(self):
        providerclass = self.__class__.__name__
        if 'Azure' in providerclass:
            return CleanAzureNics(client=self.client, dry_data=self.dry_data)
        elif 'AWS' in providerclass:
            return CleanAWSNics(client=self.client, dry_data=self.dry_data)

    @property
    def pips(self):
        providerclass = self.__class__.__name__
        if 'Azure' in providerclass:
            return CleanAzurePips(client=self.client, dry_data=self.dry_data)
        elif 'AWS' in providerclass:
            return CleanAWSPips(client=self.client, dry_data=self.dry_data)

    @property
    def images(self):
        providerclass = self.__class__.__name__
        if 'Azure' in providerclass:
            return CleanAzureImages(client=self.client, dry_data=self.dry_data)
        elif 'AWS' in providerclass:
            return CleanAWSImages(client=self.client, dry_data=self.dry_data)

    @property
    def stacks(self):
        providerclass = self.__class__.__name__
        if 'AWS' in providerclass:
            return CleanAWSStacks(client=self.client, dry_data=self.dry_data)


class AzureCleanup(providerCleanup):
    pass


class AWSCleanup(providerCleanup):
    pass


class GCECleanup(providerCleanup):
    pass


class VMWareCleanup(providerCleanup):
    pass


class PodmanCleanup(providerCleanup):
    @property
    def containers(self):
        return CleanPodmanContainers(client=self.client, dry_data=self.dry_data)
