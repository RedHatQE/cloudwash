from cloudwash.entities.providers.base import providerCleanup


class AWSCleanup(providerCleanup):

    def __init__(self, client):
        self.client = client
        super().__init__(client)
