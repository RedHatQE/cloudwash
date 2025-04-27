import json
import os
import tempfile

from cloudwash.config import settings
from cloudwash.constants import OCP_TAG_SUBSTR
from cloudwash.entities.resources.base import OCPsCleanup
from cloudwash.logger import logger
from cloudwash.utils import destroy_ocp_cluster_wrapper
from cloudwash.utils import check_installer_exists
from cloudwash.utils import dry_data
from cloudwash.utils import filter_resources_by_time_modified
from cloudwash.utils import group_ocps_by_cluster


class CleanOCPs(OCPsCleanup):
    def __init__(self, client):
        self.client = client
        self._deletable = {"ocp_clusters": [], "filtered_leftovers": []}
        self._cluster_map = {}
        self.list()

    def _set_dry(self):
        def _make_printable(resources: list):
            return {
                ocp.resource_type: [
                    r.name for r in resources if r.resource_type == ocp.resource_type
                ]
                for ocp in resources
            }

        dry_data['OCPS']['delete'] = _make_printable(self._deletable["filtered_leftovers"])
        dry_data['OCPS']['clusters'] = self._deletable["ocp_clusters"]

    def list(self):
        pass

    def remove(self):
        pass

    def prepare_cluster_metadata(self, cluster_name: str, region: str, cleanup_dir: str):
        """
        TODO Complete
        """
        # Prepare the data
        logger.info(f"\nPreparing metadata for cluster: {cluster_name}")
        cluster_metadata = {
            "aws": {
                "region": region,
                "identifier": [{f"{OCP_TAG_SUBSTR}{cluster_name}": "owned"}],
            }
        }
        metadata_file = os.path.join(cleanup_dir, "metadata.json")

        # Write the JSON to the file
        with open(metadata_file, "w") as f:
            json.dump(cluster_metadata, f)

        logger.debug(f"Metadata written to {metadata_file}")
        return metadata_file

    def cleanup(self, user_validation=False):
        if not settings.dry_run:
            check_installer_exists()
            with tempfile.TemporaryDirectory() as tmpdir:
                for cluster_name in self._deletable["ocp_clusters"]:
                    metadata_path = self.prepare_cluster_metadata(
                        cluster_name=cluster_name,
                        region=self.client.cleaning_region,
                        cleanup_dir=tmpdir,
                    )
                    destroy_ocp_cluster_wrapper(metadata_path=metadata_path, cluster_name=cluster_name, user_validation=user_validation)



class CleanAWSOcps(CleanOCPs):
    def list(self):
        resources = []
        time_threshold = settings.aws.criteria.ocps.get("SLA")

        ocp_prefixes = list(settings.aws.criteria.ocps.get("OCP_PREFIXES") or [""])
        for prefix in ocp_prefixes:
            query = " ".join(
                [f"tag.key:{OCP_TAG_SUBSTR}{prefix}*", f"region:{self.client.cleaning_region}"]
            )
            resources.extend(self.client.list_resources(query=query))

        # Filter resources by SLA before deletion
        self._cluster_map = group_ocps_by_cluster(resources=resources)
        for cluster_name in self._cluster_map.keys():
            cluster_resources = self._cluster_map[cluster_name].get("Resources")
            instances = self._cluster_map[cluster_name].get("Instances")
            leftover_ocp = False

            if instances:
                # For resources with associated EC2 Instances, filter by Instances SLA
                if filter_resources_by_time_modified(
                    time_threshold,
                    resources=instances,
                ):
                    leftover_ocp = True
                    self._deletable["filtered_leftovers"].extend(instances)
            else:
                # For resources with no associated EC2 Instances, identify as leftovers
                leftover_ocp = True

            if leftover_ocp:
                if not filter_resources_by_time_modified(time_threshold, resources=cluster_resources):
                    for r in cluster_resources:
                        print(r.date_modified)
                    import ipdb
                    ipdb.set_trace()
                # Will not collect resources recorded during the SLA time
                self._deletable["filtered_leftovers"].extend(cluster_resources)
                self._deletable["ocp_clusters"].append(cluster_name)

        # Sort resources by type and cluster by name
        self._deletable["filtered_leftovers"] = sorted(
            self._deletable["filtered_leftovers"], key=lambda x: x.resource_type
        )
        self._deletable["ocp_clusters"] = sorted(self._deletable["ocp_clusters"])
        self._set_dry()
