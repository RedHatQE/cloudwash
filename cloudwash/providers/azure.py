"""Azure CR Cleanup Utilities"""
from cloudwash.client import compute_client
from cloudwash.config import settings
from cloudwash.logger import logger
from cloudwash.utils import dry_data
from cloudwash.utils import echo_dry
from cloudwash.utils import total_running_time


def _dry_vms(all_vms):
    """Filters and returns running VMs to be deleted from all VMs"""
    _vms = {"stop": [], "delete": [], "skip": []}
    for vm in all_vms:
        # Remove the VM that's in Failed state and cant perform in assessments
        if not vm.exists:
            _vms["delete"].append(vm.name)
            continue
        # Don't assess the VM that is still in creating state
        if vm.state.lower() == "vmstate.creating":
            continue
        # Match the user defined criteria in settings to delete the VM
        if vm.name in settings.azure.exceptions.vm.vm_list:
            _vms["skip"].append(vm.name)
            continue
        elif (
            getattr(
                total_running_time(vm), "minutes", int(settings.azure.criteria.vm.sla_minutes) + 1
            )
            >= settings.azure.criteria.vm.sla_minutes
        ):
            if vm.name in settings.azure.exceptions.vm.stop_list:
                _vms["stop"].append(vm.name)
                continue
            elif vm.name.startswith(settings.azure.criteria.vm.delete_vm):
                _vms["delete"].append(vm.name)
    return _vms


def cleanup(**kwargs):
    is_dry_run = kwargs["dry_run"]

    data = ['VMS', 'NICS', 'DISCS', 'PIPS', 'RESOURCES']
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
            dry_data['VMS']['stop'] = []
            dry_data['VMS']['skip'] = []
            for items in data:
                dry_data[items]['delete'] = []

            with compute_client("azure", azure_region=region, resource_group=group) as azure_client:
                # Dry Data Collection Defs
                def dry_vms():
                    all_vms = azure_client.list_vms()
                    dry_data["VMS"] = _dry_vms(all_vms)
                    return dry_data["VMS"]

                def dry_nics():
                    rnics = []
                    if settings.azure.criteria.nic.unassigned:
                        rnics = azure_client.list_free_nics()
                        [dry_data["NICS"]["delete"].append(dnic) for dnic in rnics]
                    return rnics

                def dry_discs():
                    rdiscs = []
                    if settings.azure.criteria.disc.unassigned:
                        rdiscs = azure_client.list_free_discs()
                        [dry_data["DISCS"]["delete"].append(ddisc) for ddisc in rdiscs]
                    return rdiscs

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

                # Remove / Stop VMs
                def remove_vms(avms):
                    # Remove VMs
                    [azure_client.get_vm(vm_name).delete() for vm_name in avms["delete"]]
                    # Stop VMs
                    [azure_client.get_vm(vm_name).stop() for vm_name in avms["stop"]]

                # Actual Cleaning and dry execution
                logger.info(f"\nResources from the region and resource group: {region}/{group}")

                if kwargs["vms"] or kwargs["_all"]:
                    avms = dry_vms()
                    if not is_dry_run:
                        remove_vms(avms=avms)
                        logger.info(f"Stopped VMs: \n{avms['stop']}")
                        logger.info(f"Removed VMs: \n{avms['delete']}")
                        logger.info(f"Skipped VMs: \n{avms['skip']}")
                if kwargs["nics"] or kwargs["_all"]:
                    rnics = dry_nics()
                    if not is_dry_run and rnics:
                        azure_client.remove_nics_by_search()
                        logger.info(f"Removed NICs: \n{rnics}")
                if kwargs["discs"] or kwargs["_all"]:
                    rdiscs = dry_discs()
                    if not is_dry_run and rdiscs:
                        azure_client.remove_discs_by_search()
                        logger.info(f"Removed Discs: \n{rdiscs}")
                if kwargs["pips"] or kwargs["_all"]:
                    rpips = dry_pips()
                    if not is_dry_run and rpips:
                        azure_client.remove_pips_by_search()
                        logger.info(f"Removed PIPs: \n{rpips}")
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
