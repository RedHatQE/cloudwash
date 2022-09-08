"""ec2 CR Cleanup Utilities"""
from cloudwash.client import compute_client
from cloudwash.config import settings
from cloudwash.logger import logger
from cloudwash.utils import dry_data
from cloudwash.utils import echo_dry
from cloudwash.utils import total_running_time


def cleanup(**kwargs):

    is_dry_run = kwargs["dry_run"]
    data = ['VMS', 'DISCS', 'PIPS', 'RESOURCES', 'STACKS']
    regions = settings.aws.auth.regions
    with compute_client("aws", aws_region="us-west-2") as client:
        if "all" in regions:
            regions = client.list_regions()
    for region in regions:
        dry_data['VMS']['stop'] = []
        dry_data['VMS']['skip'] = []
        for items in data:
            dry_data[items]['delete'] = []
        with compute_client("aws", aws_region=region) as aws_client:
            # Dry Data Collection Defs
            def dry_vms():
                all_vms = aws_client.list_vms()
                for vm in all_vms:
                    if vm.name in settings.aws.exceptions.vm.vm_list:
                        dry_data["VMS"]["skip"].append(vm.name)
                        continue
                    elif total_running_time(vm).minutes >= settings.aws.criteria.vm.sla_minutes:
                        if vm.name in settings.aws.exceptions.vm.stop_list:
                            dry_data["VMS"]["stop"].append(vm.name)
                            continue
                        elif vm.name.startswith(settings.aws.criteria.vm.delete_vm):
                            dry_data["VMS"]["delete"].append(vm.name)
                return dry_data["VMS"]

            def dry_nics():
                rnics = []
                if settings.aws.criteria.nic.unassigned:
                    rnics = aws_client.get_all_unused_network_interfaces()
                    [
                        dry_data["NICS"]["delete"].append(dnic["NetworkInterfaceId"])
                        for dnic in rnics
                    ]
                return rnics

            def dry_discs():
                rdiscs = []
                if settings.aws.criteria.disc.unassigned:
                    rdiscs = aws_client.get_all_unattached_volumes()
                    [dry_data["DISCS"]["delete"].append(ddisc["VolumeId"]) for ddisc in rdiscs]
                return rdiscs

            def dry_pips():
                rpips = []
                if settings.aws.criteria.public_ip.unassigned:
                    rpips = aws_client.get_all_disassociated_addresses()
                    [dry_data["PIPS"]["delete"].append(dpip["AllocationId"]) for dpip in rpips]
                return rpips

            def dry_stacks():
                rstacks = []
                [
                    rstacks.append(stack.name)
                    for stack in aws_client.list_stacks()
                    if (
                        total_running_time(stack).minutes
                        >= settings.aws.criteria.stacks.sla_minutes
                        and stack.name.startswith(settings.aws.criteria.stacks.delete_stack)
                    )
                    and stack.name not in settings.aws.exceptions.stacks.stack_list
                ]
                [dry_data['STACKS']['delete'].append(stack) for stack in rstacks]

                return rstacks

            # Remove / Stop VMs
            def remove_vms(avms):
                # Remove VMs
                [aws_client.get_vm(vm_name).delete() for vm_name in avms["delete"]]
                # Stop VMs
                [aws_client.get_vm(vm_name).stop() for vm_name in avms["stop"]]

            # Delete CloudFormations
            def remove_stacks(stacks):
                [aws_client.get_stack(stack_name).delete() for stack_name in stacks]

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
                if not is_dry_run and rnics:
                    aws_client.remove_all_unused_nics()
                    logger.info(f"Removed NICs: \n{rnics}")
            if kwargs["discs"] or kwargs["_all"]:
                rdiscs = dry_discs()
                if not is_dry_run and rdiscs:
                    aws_client.remove_all_unused_volumes()
                    logger.info(f"Removed Discs: \n{rdiscs}")
            if kwargs["pips"] or kwargs["_all"]:
                rpips = dry_pips()
                if not is_dry_run and rpips:
                    aws_client.remove_all_unused_ips()
                    logger.info(f"Removed PIPs: \n{rpips}")
            if kwargs["stacks"] or kwargs["_all"]:
                rstacks = dry_stacks()
                if not is_dry_run:
                    remove_stacks(stacks=rstacks)
                    logger.info(f"Removed Stacks: \n{rstacks}")
            if is_dry_run:
                echo_dry(dry_data)
