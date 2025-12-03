import tempfile

from cloudwash.config import settings
from cloudwash.constants import CLUSTER_EXP_DATE_TAG
from cloudwash.constants import CLUSTER_ID_TAGS
from cloudwash.constants import CLUSTER_NAME_TAGS
from cloudwash.constants import OCP_TAG_SUBSTR
from cloudwash.entities.resources.base import OCPsCleanup
from cloudwash.logger import logger
from cloudwash.utils import check_installer_exists
from cloudwash.utils import destroy_ocp_cluster_wrapper
from cloudwash.utils import dry_data
from cloudwash.utils import filter_resources_by_time_modified
from cloudwash.utils import write_metadata_file


class LeftoverAWSOcp:
    def __init__(self, infra_id: str, region: str):
        self.infra_id = infra_id
        self.region = region
        self.associated_resources = {"Resources": [], "Instances": []}
        self._cluster_name = ""  # Extract using resources tags
        self._cluster_id = ""  # Extract using resources tags
        self._expiration_date = ""  # Extract using resources tags

    def __repr__(self):
        return (
            f'{self.infra_id}, Region: {self.region}, Instances: '
            f'{len(self.associated_resources.get("Instances"))}, other resources: '
            f'{len(self.associated_resources.get("Resources"))})'
        )

    def get_cluster_info(
        self,
    ):
        for resources_types in self.associated_resources.values():
            for resource in resources_types:
                if all([self._cluster_id, self._cluster_name, self._expiration_date]):
                    break
                if not self._expiration_date:
                    exp_date = resource.get_tag_value(key=CLUSTER_EXP_DATE_TAG)
                    if exp_date:
                        self._expiration_date = exp_date
                for name in CLUSTER_NAME_TAGS:
                    if not self._cluster_name:
                        name_tag = resource.get_tag_value(key=name)
                        if name_tag:
                            self._cluster_name = name_tag
                for id in CLUSTER_ID_TAGS:
                    if not self._cluster_id:
                        id_tag = resource.get_tag_value(key=id)
                        if id_tag:
                            self._cluster_id = id_tag

    def get_cluster_metadata(
        self,
    ):
        """
        TODO Complete
        TODO Check if we can extract HostedZoneRole, clusterDomain
        """
        # Prepare the data
        infraID = self.infra_id
        clusterName = self._cluster_name or infraID
        clusterID = self._cluster_id or infraID

        logger.info(f"\nPreparing metadata for cluster: {infraID}")

        cluster_metadata = {
            "clusterName": f"{clusterName}",
            "clusterID": f"{clusterID}",
            "infraID": f"{infraID}",
            "aws": {
                "region": self.region,
                "identifier": [{f"{OCP_TAG_SUBSTR}{infraID}": "owned"}],
            },
        }
        return cluster_metadata


class CleanOCPs(OCPsCleanup):
    def __init__(self):
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

    def cleanup(self, user_validation=False):
        if not settings.dry_run:
            check_installer_exists()
            with tempfile.TemporaryDirectory() as tmpdir:
                for cluster_name in self._deletable["ocp_clusters"]:
                    cluster = self._cluster_map[cluster_name]
                    cluster.get_cluster_info()
                    cluster.metadata = cluster.get_cluster_metadata()
                    metadata_path = write_metadata_file(
                        cluster_metadata=cluster.metadata, cleanup_dir=tmpdir
                    )
                    destroy_ocp_cluster_wrapper(
                        metadata_path=metadata_path,
                        cluster_name=cluster_name,
                        user_validation=user_validation,
                    )


class CleanAWSOcps(CleanOCPs):
    def __init__(self, client):
        self.client = client
        self.cleaning_region = self.client.cleaning_region
        super().__init__()


    def group_ocps_by_cluster(self, resources: list = None) -> dict:
        """Group different types of AWS resources under their original OCP clusters

        :param list resources: AWS resources collected by defined region and sla
        :return: A dictionary with the clusters as keys and the associated resources as values
        """
        if resources is None:
            resources = []
        clusters_map = {}

        for resource in resources:
            for key in resource.get_tags(regex=OCP_TAG_SUBSTR):
                cluster_infra_id = key.get("Key")
                if OCP_TAG_SUBSTR in cluster_infra_id:
                    # Considering the following format: "kubernetes.io/cluster/<CLUSTER_INFRA_ID>"
                    cluster_infra_id = cluster_infra_id.split(OCP_TAG_SUBSTR)[1]
                    if cluster_infra_id not in clusters_map.keys():
                        clusters_map[cluster_infra_id] = LeftoverAWSOcp(
                            infra_id=cluster_infra_id, region=self.cleaning_region
                        )

                    # Set cluster's EC2 instances
                    if hasattr(resource, 'ec2_instance'):
                        clusters_map[cluster_infra_id].associated_resources["Instances"].append(
                            resource
                        )
                    # Set resource under cluster
                    else:
                        clusters_map[cluster_infra_id].associated_resources["Resources"].append(
                            resource
                        )
        return clusters_map

    def _filter_deletable(self):
        time_threshold = settings.aws.criteria.ocps.get("SLA")
        for cluster in self._cluster_map.keys():
            resources = self._cluster_map[cluster].associated_resources.get("Resources")
            instances = self._cluster_map[cluster].associated_resources.get("Instances")
            leftover_ocp = False

            if instances:
                # For resources with associated EC2 Instances, filter by Instances SLA
                if filter_resources_by_time_modified(
                    time_threshold,
                    resources=instances,
                ):
                    leftover_ocp = True
                    # If cluster is not selected due to other resources being used,
                    # the instances will only be printed in dry run
                    self._deletable["filtered_leftovers"].extend(instances)
            else:
                # For resources with no associated EC2 Instances, consider as leftovers
                leftover_ocp = True

            if leftover_ocp:
                # Filter all cluster resources by SLA to avoid deletion of resources that are
                # in use, like EBS volume or security groups
                if filter_resources_by_time_modified(time_threshold, resources=resources):
                    # Will not collect resources recorded during the SLA time
                    self._deletable["ocp_clusters"].append(cluster)
                    self._deletable["filtered_leftovers"].extend(resources)
                else:
                    logger.info(
                        f"Found resources in use, skipping the deletion of cluster {cluster}"
                    )

    def list(self):
        resources = []

        ocp_prefixes = list(settings.aws.criteria.ocps.get("OCP_PREFIXES") or [""])
        for prefix in ocp_prefixes:
            query = " ".join(
                [f"tag.key:{OCP_TAG_SUBSTR}{prefix}*", f"region:{self.cleaning_region}"]
            )
            resources.extend(self.client.list_resources(query=query))

        # Filter resources by SLA before deletion
        self._cluster_map = self.group_ocps_by_cluster(resources=resources)
        self._filter_deletable()

        # Sort resources by type and cluster by name
        self._deletable["filtered_leftovers"] = sorted(
            self._deletable["filtered_leftovers"], key=lambda x: x.resource_type
        )
        self._deletable["ocp_clusters"] = sorted(self._deletable["ocp_clusters"])
        self._set_dry()
