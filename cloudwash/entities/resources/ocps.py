from cloudwash.config import settings
from cloudwash.entities.resources.base import OCPsCleanup
from cloudwash.utils import calculate_time_threshold
from cloudwash.utils import dry_data
from cloudwash.utils import filter_resources_by_time_modified
from cloudwash.utils import group_ocps_by_cluster
from cloudwash.utils import OCP_TAG_SUBSTR


class CleanOCPs(OCPsCleanup):
    def __init__(self, client):
        self.client = client
        self._delete = []
        self.list()

    def _set_dry(self):
        dry_data['OCPS']['delete'] = self._delete

    def list(self):
        pass

    def remove(self):
        pass

    def cleanup(self):
        if not settings.dry_run:
            self.remove()


class CleanAWSOcps(CleanOCPs):
    def list(self):
        resources = []
        time_threshold = calculate_time_threshold(time_ref=settings.aws.criteria.ocps.get("SLA"))

        ocp_prefix = list(settings.aws.criteria.ocps.get("OCP_PREFIXES") or [""])
        for prefix in ocp_prefix:
            query = " ".join(
                [f"tag.key:{OCP_TAG_SUBSTR}{prefix}*", f"region:{self.client.cleaning_region}"]
            )
            resources.extend(self.client.list_resources(query=query))

        # Prepare resources to be filtered before deletion
        cluster_map = group_ocps_by_cluster(resources=resources)
        for cluster_name in cluster_map.keys():
            cluster_resources = cluster_map[cluster_name].get("Resources")
            instances = cluster_map[cluster_name].get("Instances")

            if instances:
                # For resources with associated EC2 Instances, filter by Instances SLA
                if not filter_resources_by_time_modified(
                    time_threshold,
                    resources=instances,
                ):
                    self._delete.extend(cluster_resources)
            else:
                # For resources with no associated EC2 Instances, identify as leftovers
                self._delete.extend(
                    filter_resources_by_time_modified(time_threshold, resources=cluster_resources)
                )

        # Sort resources by type
        self._delete = sorted(self._delete, key=lambda x: x.resource_type)
        self._set_dry()
