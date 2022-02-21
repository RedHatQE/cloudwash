"""Azure CR Cleanup Utilities"""
from cloudwash.config import settings
from cloudwash.logger import logger
from cloudwash.utils import dry_data
from cloudwash.utils import echo_dry
from cloudwash.utils import total_running_time
from cloudwash.client import compute_client


def _dry_vms(all_vms):
    """Filters and returns running VMs to be deleted from all VMs"""
    _vms = {'stop': [], 'delete': []}
    for vm in all_vms:
        # Remove the VM thats in Failed state and cant perform in assessments
        if not vm.exists:
            _vms['delete'].append(vm.name)
            continue
        # Dont asses the VM that is still in creating state
        if vm.state.lower() == 'vmstate.creating':
            continue
        # Match the user defined criteria in settings to delete the VM
        if vm.name.startswith(settings.delete_vm):
            vm_running_time = getattr(total_running_time(vm), 'minutes', int(settings.sla_minutes)+1) 
            if  vm_running_time >= settings.sla_minutes:
                if vm.name in settings.providers.azure.except_vm_stop_list:
                    _vms['stop'].append(vm.name)
                    continue
                _vms['delete'].append(vm.name)
    return _vms


def cleanup(**kwargs):
    is_dry_run = kwargs['dry_run']

    with compute_client('azure') as azure_client:
        # Dry Data Collection Defs
        def dry_vms():
            all_vms = azure_client.list_vms()
            dry_data['VMS'] = _dry_vms(all_vms)
            return dry_data['VMS']

        def dry_nics():
            rnics = azure_client.list_free_nics()
            [dry_data['NICS']['delete'].append(dnic) for dnic in rnics]
            return rnics

        def dry_discs():
            rdiscs = azure_client.list_free_discs()
            [dry_data['DISCS']['delete'].append(ddisc) for ddisc in rdiscs]
            return rdiscs

        def dry_pips():
            rpips = azure_client.list_free_pip()
            [dry_data['PIPS']['delete'].append(dpip) for dpip in rpips]
            return rpips

        # Remove / Stop VMs
        def remove_vms(avms):
            # Remove VMs
            [azure_client.get_vm(vm_name).delete() for vm_name in avms['delete']]
            # Stop VMs
            [azure_client.get_vm(vm_name).stop() for vm_name in avms['stop']]

        # Actual Cleaning and dry execution
        if kwargs['vms'] or kwargs['_all']:
            avms = dry_vms()
            if not is_dry_run:
                remove_vms(avms=avms)
                logger.info(
                    f"Stopped {avms['stop']} and removed {avms['delete']} VMs from Azure Cloud.")
        if kwargs['nics'] or kwargs['_all']:
            rnics = dry_nics()
            if not is_dry_run:
                azure_client.remove_nics_by_search()
                logger.info(f'Removed following and all unused nics from Azure Cloud. \n{rnics}')
        if kwargs['discs'] or kwargs['_all']:
            rdiscs = dry_discs()
            if not is_dry_run:
                azure_client.remove_discs_by_search()
                logger.info(f'Removed following and all unused discs from Azure Cloud. \n{rdiscs}')
        if kwargs['pips'] or kwargs['_all']:
            rpips = dry_pips()
            if not is_dry_run:
                azure_client.remove_pips_by_search()
                logger.info(f'Removed following and all unused pips from Azure Cloud. \n{rpips}')
        if is_dry_run:
            echo_dry(dry_data)
