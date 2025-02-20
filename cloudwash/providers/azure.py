"""Azure CR Cleanup Utilities"""
from copy import deepcopy

from cloudwash.client import compute_client
from cloudwash.config import settings
from cloudwash.constants import azure_data as data
from cloudwash.entities.providers import AzureCleanup
from cloudwash.logger import logger
from cloudwash.utils import create_html
from cloudwash.utils import dry_data
from cloudwash.utils import echo_dry


def cleanup(**kwargs):
    is_dry_run = kwargs["dry_run"]
    dry_data['PROVIDER'] = "AZURE"
    regions = settings.azure.auth.regions
    groups = settings.azure.auth.resource_groups
    all_data = []

    if "all" in regions:
        # non-existent RG can be chosen for query
        # as it's never accessed and is only stored within wrapper
        with compute_client("azure", azure_region="us-west", resource_group="foo") as azure_client:
            regions = list(zip(*azure_client.list_region()))[0]
    for region in regions:
        dry_data['REGION'] = region
        if "all" in groups:
            # non-existent RG can be chosen for query
            # as it's never accessed and is only stored within wrapper
            with compute_client("azure", azure_region=region, resource_group="foo") as azure_client:
                groups = azure_client.list_resource_groups()

        for group in groups:
            dry_data['GROUP'] = group
            for items in data:
                dry_data[items]['delete'] = []

            with compute_client("azure", azure_region=region, resource_group=group) as azure_client:
                azurecleanup = AzureCleanup(client=azure_client)

                def dry_resources(hours_old=None):
                    dry_data["RESOURCES"]["delete"] = azure_client.list_resources_from_hours_old(
                        hours_old=hours_old
                        or (settings.azure.criteria.resource_group.resources_sla_minutes / 60)
                    )
                    return dry_data["RESOURCES"]["delete"]

                # Actual Cleaning and dry execution
                logger.info(f"\nResources from the region and resource group: {region}/{group}")

                if kwargs["vms"] or kwargs["_all"]:
                    azurecleanup.vms.cleanup()
                if kwargs["nics"] or kwargs["_all"]:
                    azurecleanup.nics.cleanup()
                if kwargs["discs"] or kwargs["_all"]:
                    azurecleanup.discs.cleanup()
                if kwargs["pips"] or kwargs["_all"]:
                    azurecleanup.pips.cleanup()
                if kwargs["images"] or kwargs["_all"]:
                    azurecleanup.images.cleanup()

                if kwargs["_all_rg"]:
                    sla_time = settings.azure.criteria.resource_group.resources_sla_minutes

                    # Exception list has priority
                    if group in settings.azure.exceptions.group.rg_list:
                        continue

                    if settings.azure.criteria.resource_group.logic == "AND":
                        if group.startswith(settings.azure.criteria.resource_group.delete_group):
                            rres = dry_resources(sla_time)
                    elif settings.azure.criteria.resource_group.logic == "OR":
                        if group.startswith(settings.azure.criteria.resource_group.delete_group):
                            sla_time = 0

                        rres = dry_resources(sla_time)
                    else:
                        raise Exception("Invalid logic for resource group cleanup")

                    if not is_dry_run and rres:
                        azure_client.remove_resource_group_of_old_resources(
                            hours_old=(sla_time / 60)
                        )
                        logger.info(f"Removed Resources: \n{rres}")
                if is_dry_run:
                    echo_dry(dry_data)
                    all_data.append(deepcopy(dry_data))
    if is_dry_run:
        create_html(dry_data['PROVIDER'], all_data)
