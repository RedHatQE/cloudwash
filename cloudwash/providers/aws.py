"""ec2 CR Cleanup Utilities"""
from cloudwash.client import compute_client
from cloudwash.config import settings
from cloudwash.constants import aws_data as data
from cloudwash.entities.providers import AWSCleanup
from cloudwash.logger import logger
from cloudwash.utils import create_html
from cloudwash.utils import DryData
from cloudwash.utils import print_dry_data


def cleanup(**kwargs):
    is_dry_run = kwargs.get("dry_run", False)
    dry_data = DryData()
    dry_data['PROVIDER'] = "AWS"
    regions = settings.aws.auth.regions
    all_data = []

    if kwargs["ocps"]:
        aws_client_region = settings.aws.criteria.ocps.ocp_client_region
        with compute_client("aws", aws_region=aws_client_region) as aws_ocp_client:
            if "all" in regions:
                regions = aws_ocp_client.list_regions()
            awscleanup = AWSCleanup(client=aws_ocp_client, dry_data=dry_data)
            for region in regions:
                dry_data['REGION'] = region
                aws_ocp_client.cleaning_region = region
                # Emptying the dry data for previous region everytime
                for items in data:
                    dry_data.reset_resource(items)
                logger.info(f"\nResources from the region: {region}")
                awscleanup.ocps.cleanup()
                print_dry_data(dry_data, is_dry_run, all_data)
    else:
        if "all" in regions:
            with compute_client("aws", aws_region="us-west-2") as client:
                regions = client.list_regions()
        for region in regions:
            dry_data['REGION'] = region
            # Emptying the dry data for previous region everytime
            for items in data:
                dry_data.reset_resource(items)
            with compute_client("aws", aws_region=region) as aws_client:
                awscleanup = AWSCleanup(client=aws_client, dry_data=dry_data)
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
                print_dry_data(dry_data, is_dry_run, all_data)
    if is_dry_run:
        create_html(dry_data['PROVIDER'], all_data)
