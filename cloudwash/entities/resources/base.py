from abc import ABC
from abc import abstractmethod


class ResourceCleanup(ABC):
    @abstractmethod
    def cleanup(self):
        pass

    @abstractmethod
    def list(self):
        pass

    @abstractmethod
    def _set_dry(self):
        pass


class OCPsCleanup(ResourceCleanup):
    @abstractmethod
    def list(self):
        pass

    @abstractmethod
    def cleanup(self):
        pass

    @abstractmethod
    def remove(self):
        pass

    @abstractmethod
    def _set_dry(self):
        pass


class DiscsCleanup(ResourceCleanup):
    @abstractmethod
    def list(self):
        pass

    @abstractmethod
    def cleanup(self):
        pass

    @abstractmethod
    def remove(self):
        pass

    @abstractmethod
    def _set_dry(self):
        pass


class ImagesCleanup(ResourceCleanup):
    @abstractmethod
    def list(self):
        pass

    @abstractmethod
    def cleanup(self):
        pass

    @abstractmethod
    def remove(self):
        pass

    @abstractmethod
    def _set_dry(self):
        pass


class NicsCleanup(ResourceCleanup):
    @abstractmethod
    def list(self):
        pass

    @abstractmethod
    def cleanup(self):
        pass

    @abstractmethod
    def remove(self):
        pass

    @abstractmethod
    def _set_dry(self):
        pass


class PipsCleanup(ResourceCleanup):
    @abstractmethod
    def list(self):
        pass

    @abstractmethod
    def cleanup(self):
        pass

    @abstractmethod
    def remove(self):
        pass

    @abstractmethod
    def _set_dry(self):
        pass


class StacksCleanup(ResourceCleanup):
    @abstractmethod
    def list(self):
        pass

    @abstractmethod
    def cleanup(self):
        pass

    @abstractmethod
    def remove(self):
        pass

    @abstractmethod
    def _set_dry(self):
        pass


class VMsCleanup(ResourceCleanup):
    @abstractmethod
    def list(self):
        pass

    @abstractmethod
    def cleanup(self):
        pass

    @abstractmethod
    def stop(self):
        pass

    @abstractmethod
    def remove(self):
        pass

    @abstractmethod
    def skip(self):
        pass

    @abstractmethod
    def _set_dry(self):
        pass


class ContainerCleanup(ResourceCleanup):
    @abstractmethod
    def list(self):
        pass

    @abstractmethod
    def cleanup(self):
        pass

    @abstractmethod
    def stop(self):
        pass

    @abstractmethod
    def remove(self):
        pass

    @abstractmethod
    def skip(self):
        pass

    @abstractmethod
    def _set_dry(self):
        pass


class ResourceCleanupManager:
    def __init__(self):
        self.resources = []

    def add(self, resource):
        self.resources.append(resource)

    def remove(self):
        for resource in self.resources:
            resource.remove()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.remove()
        return False
