"""GCE CR Cleanup Utilities"""
from cloudwash.config import settings
from cloudwash.logger import logger
from cloudwash.utils import dry_data
from cloudwash.utils import echo_dry
from cloudwash.utils import gce_zones
from cloudwash.utils import total_running_time
from cloudwash.client import compute_client


def cleanup(**kwargs):
    is_dry_run = kwargs['dry_run']

    with compute_client('gce') as gce_client:
        if kwargs['vms'] or kwargs['_all']:
            allvms = gce_client.list_vms(zones=gce_zones())
            for vm in allvms:
                if vm.name.startswith(settings.delete_vm) and total_running_time(vm).minutes >= settings.sla_minutes:
                    if vm.name in settings.providers.gce.except_vm_stop_list:
                        dry_data['VMS']['stop'].append(vm.name)
                        if not is_dry_run:
                            try:
                                vm.stop()
                            except TypeError:
                                logger.info(f'GCE VM \'{vm}\' is force stopped, since its listed in exception stop list.')
                            except Exception:
                                logger.exception(f'Could not stop the GCE VM - {vm.name}')
                        continue
                    dry_data['VMS']['delete'].append(vm.name)
                    if not is_dry_run:
                        try:
                            vm.delete()
                        # Currently there as an issue with GCE API while deleting, stopping the VM
                        # That it throws TypeError, hence catching that error here
                        # Remove it once its fixed
                        except TypeError:
                            logger.info(f'GCE VM \'{vm.name}\' is deleted!')
                        except Exception:
                            logger.exception(f'Could not delete the GCE VM - {vm.name}')
        if kwargs['nics'] or kwargs['_all']:
            logger.warning('WrapanAPI does not supports NICs operation for GCE yet!')
        if kwargs['discs'] or kwargs['_all']:
            logger.warning('WrapanAPI does not supports DISCs operation for GCE yet!')
        if is_dry_run:
            echo_dry(dry_data)
