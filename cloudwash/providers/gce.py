"""GCE CR Cleanup Utilities"""
from cloudwash.client import compute_client
from cloudwash.config import settings
from cloudwash.logger import logger
from cloudwash.utils import dry_data
from cloudwash.utils import echo_dry
from cloudwash.utils import gce_zones
from cloudwash.utils import total_running_time


def cleanup(**kwargs):
    is_dry_run = kwargs["dry_run"]

    with compute_client("gce") as gce_client:
        if kwargs["vms"] or kwargs["_all"]:
            allvms = gce_client.list_vms(zones=gce_zones())
            for vm in allvms:
                if vm.name in settings.gce.exceptions.vm.vm_list:
                    dry_data["VMS"]["skip"].append(vm.name)
                    continue
                elif total_running_time(vm).minutes >= settings.gce.criteria.vm.sla_minutes:
                    if vm.name in settings.gce.exceptions.vm.stop_list:
                        dry_data["VMS"]["stop"].append(vm.name)
                        if not is_dry_run:
                            try:
                                vm.stop()
                            except TypeError:
                                logger.info(f"Stopped VM: {vm.name}")
                            except Exception:
                                logger.exception(f"Error stopping VM {vm.name}")
                        continue
                    elif vm.name.startswith(settings.gce.criteria.vm.delete_vm):
                        dry_data["VMS"]["delete"].append(vm.name)
                        if not is_dry_run:
                            try:
                                vm.delete()
                            # There as an issue with GCE API while deleting/stopping the VM
                            # That it throws TypeError, hence catching that error here
                            # Remove it once its fixed
                            except TypeError:
                                logger.info(f"Deleted VM: {vm.name}")
                            except Exception:
                                logger.exception(f"Error deleting VM {vm.name}")
        if kwargs["nics"] or kwargs["_all"]:
            logger.warning(
                "Cloudwash dependency 'WrapanAPI' does not supports NICs operation for GCE yet!"
            )
        if kwargs["discs"] or kwargs["_all"]:
            logger.warning(
                "Cloudwash dependency 'WrapanAPI' does not supports DISCs operation for GCE yet!"
            )
        if is_dry_run:
            echo_dry(dry_data)
