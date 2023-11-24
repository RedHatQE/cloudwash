"""VMware CR Cleanup Utilities"""
from cloudwash.client import compute_client
from cloudwash.config import settings
from cloudwash.logger import logger
from cloudwash.utils import dry_data
from cloudwash.utils import echo_dry
from cloudwash.utils import total_running_time


def cleanup(**kwargs):
    is_dry_run = kwargs["dry_run"]

    with compute_client("vmware") as client:
        if kwargs["vms"] or kwargs["_all"]:
            allvms = client.list_vms()
            for vm in allvms:
                if vm.name in settings.vmware.exceptions.vm.vm_list:
                    dry_data["VMS"]["skip"].append(vm.name)
                    continue
                elif total_running_time(vm).minutes >= settings.vmware.criteria.vm.sla_minutes:
                    if vm.name in settings.vmware.exceptions.vm.stop_list:
                        dry_data["VMS"]["stop"].append(vm.name)
                        if not is_dry_run:
                            try:
                                vm.stop()
                                logger.info(f"Stopped VM: {vm.name}")
                            except Exception:
                                logger.exception(f"Error stopping VM {vm.name}")
                        continue
                    elif vm.name.startswith(settings.vmware.criteria.vm.delete_vm):
                        dry_data["VMS"]["delete"].append(vm.name)
                        if not is_dry_run:
                            try:
                                vm.delete()
                                logger.info(f"Deleted VM: {vm.name}")
                            except Exception:
                                logger.exception(f"Error deleting VM {vm.name}")
        if kwargs["nics"] or kwargs["_all"]:
            logger.warning(
                "Cloudwash dependency 'WrapanAPI' does not supports NICs operation for VMware yet!"
            )
        if kwargs["discs"] or kwargs["_all"]:
            logger.warning(
                "Cloudwash dependency 'WrapanAPI' does not supports DISCs operation for VMware yet!"
            )
        if is_dry_run:
            echo_dry(dry_data)
