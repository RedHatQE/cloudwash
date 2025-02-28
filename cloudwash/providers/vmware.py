"""VMWare CR Cleanup Utilities"""
from copy import deepcopy

from cloudwash.client import compute_client
from cloudwash.constants import vmware_data as data
from cloudwash.entities.providers import VMWareCleanup
from cloudwash.logger import logger
from cloudwash.utils import create_html
from cloudwash.utils import dry_data
from cloudwash.utils import echo_dry


def cleanup(**kwargs):
    is_dry_run = kwargs.get("dry_run", False)
    dry_data['PROVIDER'] = "VMWARE"
    all_data = []
    if kwargs["nics"] or kwargs["_all"]:
        logger.warning("Cloudwash does not supports NICs operation for VMWare yet!")
    if kwargs["discs"] or kwargs["_all"]:
        logger.warning("Cloudwash does not supports DISCs operation for VMWare yet!")

    with compute_client("vmware") as vmware_client:
        for items in data:
            dry_data[items]['delete'] = []
        vmware_cleanup = VMWareCleanup(client=vmware_client)
        if kwargs["vms"] or kwargs["_all"]:
            vmware_cleanup.vms.cleanup()
        if is_dry_run:
            echo_dry(dry_data)
            all_data.append(deepcopy(dry_data))
    if is_dry_run:
        create_html(dry_data['PROVIDER'], all_data)
