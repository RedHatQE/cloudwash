from cloudwash.config import settings
from cloudwash.entities.resources.base import ImagesCleanup
from cloudwash.logger import logger
from cloudwash.utils import dry_data


class CleanImages(ImagesCleanup):
    def __init__(self, client):
        self.client = client
        self._delete = []
        self._stop = []
        self._skip = []
        self.list()

    def _set_dry(self):
        # ImagesContainer = namedtuple('ImagesCotainer', ['delete', 'stop', 'skip'])
        # return ImagesContainer(self._delete, self._stop, self._skip)
        dry_data['IMAGES']['delete'] = self._delete

    def list(self):
        pass

    def remove(self):
        pass

    def cleanup(self):
        if not settings.dry_run:
            self.remove()


class CleanAWSImages(CleanImages):
    def remove(self):
        self.client.delete_images(image_list=self._delete)
        logger.info(f"Removed Images: \n{self._delete}")

    def list(self):
        if settings.aws.criteria.image.unassigned:
            rimages = self.client.list_templates(executable_by_me=False, owned_by_me=True)
            free_images = self.client.list_free_images(
                image_list=[image.raw.image_id for image in rimages]
            )
            remove_images = [
                image for image in free_images if image not in settings.aws.exceptions.images
            ]
            if settings.aws.criteria.image.delete_image:
                remove_images = [
                    image
                    for image in remove_images
                    if image.startswith(settings.aws.criteria.image.delete_image)
                ]
            self._delete.extend(remove_images)
        self._set_dry()


class CleanAzureImages(CleanImages):
    def remove(self):
        self.client.delete_compute_image_by_resource_group(image_list=self._delete)
        logger.info(f"Removed Images: \n{self._delete}")

    def list(self):
        if settings.azure.criteria.image.unassigned:
            images_list = self.client.list_compute_images_by_resource_group(free_images=True)
            image_names = [image.name for image in images_list]
            # Filter out the images not to be removed.
            remove_images = [
                image for image in image_names if image not in settings.azure.exceptions.images
            ]
            if settings.azure.criteria.image.delete_image:
                remove_images = [
                    image
                    for image in remove_images
                    if image.startswith(settings.azure.criteria.image.delete_image)
                ]
            self._delete.extend(remove_images)
        self._set_dry()
