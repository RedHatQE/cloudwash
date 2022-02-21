import wrapanapi
import json

from contextlib import contextmanager
from cloudwash.config import settings


@contextmanager
def compute_client(compute_resource):
    """The context manager for compute resource client to initiate and disconnect

    :param str compute_resource: The compute resource name
    """
    if compute_resource == 'azure':
        client = wrapanapi.AzureSystem(
            username=settings.providers.azure.username, password=settings.providers.azure.password,
            tenant_id=settings.providers.azure.tenant_id, subscription_id=settings.providers.azure.subscription_id,
            provisioning={
                'resource_group': settings.providers.azure.resource_group,
                'template_container': None,
                'region_api': settings.providers.azure.region}
        )
    elif compute_resource == 'gce':
        client = wrapanapi.GoogleCloudSystem(
            project=settings.providers.gce.project_id,
            service_account=json.loads(settings.providers.gce.service_account)
        )
    elif compute_resource == 'ec2':
        client = wrapanapi.EC2System(
            username=settings.providers.ec2.username,
            password=settings.providers.ec2.password,
            region=settings.providers.ec2.region
        )
    else:
        raise ValueError(
            f'{compute_resource} is an incorrect value. It should be one of azure or gce or ec2')

    try:
        yield client
    finally:
        client.disconnect()
