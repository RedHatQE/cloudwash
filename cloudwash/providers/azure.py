"""Azure CR Cleanup Utilities"""
from cloudwash.client import compute_client
from cloudwash.config import settings
from cloudwash.entities.providers import AzureCleanup
from cloudwash.logger import logger
from cloudwash.utils import dry_data
from cloudwash.utils import echo_dry


def cleanup(**kwargs):
    is_dry_run = kwargs["dry_run"]

    data = ['VMS', 'NICS', 'DISCS', 'IMAGES', 'PIPS', 'RESOURCES']
    regions = settings.azure.auth.regions
    groups = settings.azure.auth.resource_groups

    if "all" in regions:
        # non-existent RG can be chosen for query
        # as it's never accessed and is only stored within wrapper
        with compute_client("azure", azure_region="us-west", resource_group="foo") as azure_client:
            regions = list(zip(*azure_client.list_region()))[0]

    for region in regions:
        if "all" in groups:
            # non-existent RG can be chosen for query
            # as it's never accessed and is only stored within wrapper
            with compute_client("azure", azure_region=region, resource_group="foo") as azure_client:
                groups = azure_client.list_resource_groups()

        for group in groups:
            for items in data:
                dry_data[items]['delete'] = []

            with compute_client("azure", azure_region=region, resource_group=group) as azure_client:
                azurecleanup = AzureCleanup(client=azure_client)

                def dry_nics():
                    rnics = []
                    if settings.azure.criteria.nic.unassigned:
                        rnics = azure_client.list_free_nics()
                        [dry_data["NICS"]["delete"].append(dnic) for dnic in rnics]
                    return rnics

                def dry_pips():
                    rpips = []
                    if settings.azure.criteria.public_ip.unassigned:
                        rpips = azure_client.list_free_pip()
                        [dry_data["PIPS"]["delete"].append(dpip) for dpip in rpips]
                    return rpips

                def dry_resources(hours_old=None):
                    dry_data["RESOURCES"]["delete"] = azure_client.list_resources_from_hours_old(
                        hours_old=hours_old
                        or (settings.azure.criteria.resource_group.resources_sla_minutes / 60)
                    )
                    return dry_data["RESOURCES"]["delete"]

                def dry_images():
                    remove_images = []
                    if settings.azure.criteria.image.unassigned:
                        images_list = azure_client.list_compute_images_by_resource_group(
                            free_images=True
                        )
                        image_names = [image.name for image in images_list]
                        # Filter out the images not to be removed.
                        remove_images = [
                            image
                            for image in image_names
                            if image not in settings.azure.exceptions.images
                        ]
                        if settings.azure.criteria.image.delete_image:
                            remove_images = [
                                image
                                for image in remove_images
                                if image.startswith(settings.azure.criteria.image.delete_image)
                            ]
                        dry_data["IMAGES"]["delete"].extend(remove_images)
                    return remove_images

                # Actual Cleaning and dry execution
                logger.info(f"\nResources from the region and resource group: {region}/{group}")

                if kwargs["vms"] or kwargs["_all"]:
                    azurecleanup.vms.cleanup()
                if kwargs["nics"] or kwargs["_all"]:
                    rnics = dry_nics()
                    if not is_dry_run and rnics:
                        azure_client.remove_nics_by_search()
                        logger.info(f"Removed NICs: \n{rnics}")
                if kwargs["discs"] or kwargs["_all"]:
                    azurecleanup.discs.cleanup()
                if kwargs["pips"] or kwargs["_all"]:
                    rpips = dry_pips()
                    if not is_dry_run and rpips:
                        azure_client.remove_pips_by_search()
                        logger.info(f"Removed PIPs: \n{rpips}")
                if kwargs["images"] or kwargs["_all"]:
                    rimages = dry_images()
                    if not is_dry_run and rimages:
                        azure_client.delete_compute_image_by_resource_group(image_list=rimages)
                        logger.info(f"Removed Images: \n{rimages}")

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
