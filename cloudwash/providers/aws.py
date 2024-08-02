"""ec2 CR Cleanup Utilities"""
from cloudwash.client import compute_client
from cloudwash.config import settings
from cloudwash.constants import aws_data as data
from cloudwash.entities.providers import AWSCleanup
from cloudwash.logger import logger
from cloudwash.utils import dry_data
from cloudwash.utils import echo_dry


def cleanup(**kwargs):
    is_dry_run = kwargs.get("dry_run", False)
    dry_data['PROVIDER'] = "AWS"
    regions = settings.aws.auth.regions
    if "all" in regions:
        with compute_client("aws", aws_region="us-west-2") as client:
            regions = client.list_regions()
    for region in regions:
        for items in data:
            dry_data[items]['delete'] = []
        with compute_client("aws", aws_region=region) as aws_client:
            awscleanup = AWSCleanup(client=aws_client)
            # Actual Cleaning and dry execution
            logger.info(f"\nResources from the region: {region}")
            if kwargs["vms"] or kwargs["_all"]:
                awscleanup.vms.cleanup()
            if kwargs["nics"] or kwargs["_all"]:
                awscleanup.nics.cleanup()
            if kwargs["discs"] or kwargs["_all"]:
                awscleanup.discs.cleanup()
            if kwargs["pips"] or kwargs["_all"]:
                awscleanup.pips.cleanup()
            if kwargs["images"] or kwargs["_all"]:
                awscleanup.images.cleanup()
            if kwargs["stacks"] or kwargs["_all"]:
                awscleanup.stacks.cleanup()
            if is_dry_run:
                echo_dry(dry_data)
