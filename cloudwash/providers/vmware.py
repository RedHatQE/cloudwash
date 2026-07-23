"""VMWare CR Cleanup Utilities"""
from cloudwash.client import compute_client
from cloudwash.constants import vmware_data as data
from cloudwash.entities.providers import VMWareCleanup
from cloudwash.logger import logger
from cloudwash.utils import create_html
from cloudwash.utils import DryData
from cloudwash.utils import print_dry_data


def cleanup(**kwargs):
    is_dry_run = kwargs.get("dry_run", False)
    dry_data = DryData()
    dry_data['PROVIDER'] = "VMWARE"
    all_data = []
    if kwargs["nics"] or kwargs["_all"]:
        logger.warning("Cloudwash does not supports NICs operation for VMWare yet!")
    if kwargs["discs"] or kwargs["_all"]:
        logger.warning("Cloudwash does not supports DISCs operation for VMWare yet!")

    with compute_client("vmware") as vmware_client:
        for items in data:
            dry_data.reset_resource(items)
        vmware_cleanup = VMWareCleanup(client=vmware_client, dry_data=dry_data)
        if kwargs["vms"] or kwargs["_all"]:
            vmware_cleanup.vms.cleanup()
        print_dry_data(dry_data, is_dry_run, all_data)
    if is_dry_run:
        create_html(dry_data['PROVIDER'], all_data)
