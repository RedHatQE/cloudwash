from cloudwash.config import settings
from cloudwash.entities.resources.base import StacksCleanup
from cloudwash.logger import logger
from cloudwash.utils import dry_data
from cloudwash.utils import total_running_time


class CleanStacks(StacksCleanup):
    def __init__(self, client):
        self.client = client
        self._delete = []
        self.list()

    def _set_dry(self):
        dry_data['STACKS']['delete'] = self._delete

    def list(self):
        pass

    def remove(self):
        pass

    def cleanup(self):
        if not settings.dry_run:
            self.remove()


class CleanAWSStacks(CleanStacks):
    def list(self):
        rstacks = []
        [
            rstacks.append(stack.name)
            for stack in self.client.list_stacks()
            if (
                total_running_time(stack).minutes >= settings.aws.criteria.stacks.sla_minutes
                and stack.name.startswith(settings.aws.criteria.stacks.delete_stack)
            )
            and stack.name not in settings.aws.exceptions.stacks.stack_list
        ]
        self._delete.extend(rstacks)
        self._set_dry()

    def remove(self):
        for stack_name in self._delete:
            self.client.get_stack(stack_name).delete()
        logger.info(f"Removed Stacks: \n{self._delete}")
