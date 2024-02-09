from cloudwash.config import settings
from cloudwash.entities.resources.base import VMsCleanup
from cloudwash.logger import logger
from cloudwash.utils import dry_data
from cloudwash.utils import total_running_time


class CleanVMs(VMsCleanup):
    def __init__(self, client):
        self.client = client
        self._delete = []
        self._stop = []
        self._skip = []
        self.list()

    def _set_dry(self):
        # VMsContainer = namedtuple('VMsCotainer', ['delete', 'stop', 'skip'])
        # return VMsContainer(self._delete, self._stop, self._skip)
        dry_data['VMS']['delete'] = self._delete
        dry_data['VMS']['stop'] = self._stop
        dry_data['VMS']['skip'] = self._skip

    def list(self):
        pass

    def remove(self):
        for vm_name in self._delete:
            self.client.get_vm(vm_name).delete()
        logger.info(f"Removed VMs: \n{self._delete}")

    def stop(self):
        for vm_name in self._stop:
            self.client.get_vm(vm_name).stop()
        logger.info(f"Stopped VMs: \n{self._stop}")

    def skip(self):
        logger.info(f"Skipped VMs: \n{self._skip}")

    def cleanup(self):
        if not settings.dry_run:
            self.remove()
            self.stop()
            self.skip()


class CleanAWSVms(CleanVMs):
    def list(self):
        all_vms = self.client.list_vms()

        for vm in all_vms:
            if vm.name in settings.aws.exceptions.vm.vm_list:
                self._skip.append(vm.name)
                continue

            elif total_running_time(vm).minutes >= settings.aws.criteria.vm.sla_minutes:
                if vm.name in settings.aws.exceptions.vm.stop_list:
                    self._stop.append(vm.name)
                    continue

                elif vm.name.startswith(settings.aws.criteria.vm.delete_vm):
                    self._delete.append(vm.name)
        self._set_dry()


class CleanAzureVMs(CleanVMs):
    def list(self):
        all_vms = self.client.list_vms()

        for vm in all_vms:
            if not vm.exists:
                self._delete.append(vm.name)
                continue
            # Don't assess the VM that is still in creating state
            if vm.state.lower() == "vmstate.creating":
                continue
            # Match the user defined criteria in settings to delete the VM
            if vm.name in settings.azure.exceptions.vm.vm_list:
                self._skip.append(vm.name)
            elif (
                getattr(
                    total_running_time(vm),
                    "minutes",
                    int(settings.azure.criteria.vm.sla_minutes) + 1,
                )
                >= settings.azure.criteria.vm.sla_minutes
            ):
                if vm.name in settings.azure.exceptions.vm.stop_list:
                    self._stop.append(vm.name)
                    continue
                elif vm.name.startswith(settings.azure.criteria.vm.delete_vm):
                    self._delete.append(vm.name)
        self._set_dry()
