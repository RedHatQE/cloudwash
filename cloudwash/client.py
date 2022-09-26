import json
from contextlib import contextmanager

import wrapanapi

from cloudwash.config import settings


@contextmanager
def compute_client(compute_resource, **kwargs):
    """The context manager for compute resource client to initiate and disconnect
    :param str compute_resource: The compute resource name
    """
    if compute_resource == "azure":
        client = wrapanapi.AzureSystem(
            username=settings.azure.auth.client_id,
            password=settings.azure.auth.secret_id,
            tenant_id=settings.azure.auth.tenant_id,
            subscription_id=settings.azure.auth.subscription_id,
            provisioning={
                "resource_group": settings.azure.auth.resource_group,
                "template_container": None,
                "region_api": settings.azure.auth.region,
            },
        )
    elif compute_resource == "gce":
        client = wrapanapi.GoogleCloudSystem(
            project=settings.gce.auth.project_id,
            service_account=json.loads(settings.gce.auth.service_account),
        )
    elif compute_resource == "aws":
        client = wrapanapi.EC2System(
            username=settings.aws.auth.access_key,
            password=settings.aws.auth.secret_key,
            region=kwargs['aws_region'],
        )
    else:
        raise ValueError(
            f"{compute_resource} is an incorrect value. It should be one of azure or gce or ec2"
        )

    try:
        yield client
    finally:
        client.disconnect()
