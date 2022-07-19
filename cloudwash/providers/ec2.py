"""ec2 CR Cleanup Utilities"""
from cloudwash.client import compute_client
from cloudwash.config import settings
from cloudwash.logger import logger
from cloudwash.utils import dry_data
from cloudwash.utils import echo_dry
from cloudwash.utils import total_running_time


def cleanup(**kwargs):

    is_dry_run = kwargs["dry_run"]
    data = ['VMS', 'DISCS', 'PIPS', 'RESOURCES']
    regions = settings.providers.ec2.regions
    with compute_client("ec2", ec2_region="us-west-2") as client:
        if "all" in regions:
            regions = client.list_regions()
    for region in regions:
        dry_data['VMS']['stop'] = []
        dry_data['VMS']['skip'] = []
        for items in data:
            dry_data[items]['delete'] = []
        with compute_client("ec2", ec2_region=region) as ec2_client:
            # Dry Data Collection Defs
            def dry_vms():
                all_vms = ec2_client.list_vms()
                for vm in all_vms:
                    if vm.name in settings.providers.ec2.except_vm_list:
                        dry_data["VMS"]["skip"].append(vm.name)
                        continue
                    elif total_running_time(vm).minutes >= settings.sla_minutes:
                        if vm.name in settings.providers.ec2.except_vm_stop_list:
                            dry_data["VMS"]["stop"].append(vm.name)
                            continue
                        elif vm.name.startswith(settings.delete_vm):
                            dry_data["VMS"]["delete"].append(vm.name)
                return dry_data["VMS"]

            def dry_nics():
                rnics = ec2_client.get_all_unused_network_interfaces()
                [dry_data["NICS"]["delete"].append(dnic["NetworkInterfaceId"]) for dnic in rnics]
                return dry_data["NICS"]["delete"]

            def dry_discs():
                rdiscs = ec2_client.get_all_unattached_volumes()
                [dry_data["DISCS"]["delete"].append(ddisc["VolumeId"]) for ddisc in rdiscs]
                return dry_data["DISCS"]["delete"]

            def dry_pips():
                rpips = ec2_client.get_all_disassociated_addresses()
                [dry_data["PIPS"]["delete"].append(dpip["AllocationId"]) for dpip in rpips]
                return dry_data["PIPS"]["delete"]

            # Remove / Stop VMs
            def remove_vms(avms):
                # Remove VMs
                [ec2_client.get_vm(vm_name).delete() for vm_name in avms["delete"]]
                # Stop VMs
                [ec2_client.get_vm(vm_name).stop() for vm_name in avms["stop"]]

            # Actual Cleaning and dry execution
            logger.info(f"\nResources from the region: {region}")
            if kwargs["vms"] or kwargs["_all"]:
                avms = dry_vms()
                if not is_dry_run:
                    remove_vms(avms=avms)
                    logger.info(f"Stopped VMs: \n{avms['stop']}")
                    logger.info(f"Removed VMs: \n{avms['delete']}")
                    logger.info(f"Skipped VMs: \n{avms['skip']}")
            if kwargs["nics"] or kwargs["_all"]:
                rnics = dry_nics()
                if not is_dry_run:
                    ec2_client.remove_all_unused_nics()
                    logger.info(f"Removed NICs: \n{rnics}")
            if kwargs["discs"] or kwargs["_all"]:
                rdiscs = dry_discs()
                if not is_dry_run:
                    ec2_client.remove_all_unused_volumes()
                    logger.info(f"Removed Discs: \n{rdiscs}")
            if kwargs["pips"] or kwargs["_all"]:
                rpips = dry_pips()
                if not is_dry_run:
                    ec2_client.remove_all_unused_ips()
                    logger.info(f"Removed PIPs: \n{rpips}")
            if is_dry_run:
                echo_dry(dry_data)
