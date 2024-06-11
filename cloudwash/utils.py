"""Common utils for cleanup activities of all CRs"""
from collections import namedtuple
from datetime import datetime

import dateparser
import pytz
from wrapanapi.systems.ec2 import ResourceExplorerResource

from cloudwash.logger import logger

OCP_TAG_SUBSTR = "kubernetes.io/cluster/"

_vms_dict = {"VMS": {"delete": [], "stop": [], "skip": []}}
dry_data = {
    "NICS": {"delete": []},
    "DISCS": {"delete": []},
    "PIPS": {"delete": []},
    "OCPS": {"delete": []},
    "RESOURCES": {"delete": []},
    "STACKS": {"delete": []},
    "IMAGES": {"delete": []},
}

dry_data.update(_vms_dict)


def echo_dry(dry_data=None) -> None:
    """Prints and Logs the per resource cleanup data on STDOUT and logfile

    :param dict dry_data: The deletable resources dry data of a Compute Resource,
        it follows the format of module scoped `dry_data` variable in this module
    """
    logger.info("\n=========== DRY SUMMARY ============\n")
    deletable_vms = dry_data["VMS"]["delete"]
    stopable_vms = dry_data["VMS"]["stop"]
    skipped_vms = dry_data["VMS"]["skip"]
    deletable_discs = dry_data["DISCS"]["delete"]
    deletable_nics = dry_data["NICS"]["delete"]
    deletable_images = dry_data["IMAGES"]["delete"]
    deletable_pips = dry_data["PIPS"]["delete"] if "PIPS" in dry_data else None
    deletable_ocps = {
        ocp.resource_type: [
            r.name for r in dry_data["OCPS"]["delete"] if r.resource_type == ocp.resource_type
        ]
        for ocp in dry_data["OCPS"]["delete"]
    }
    deletable_resources = dry_data["RESOURCES"]["delete"]
    deletable_stacks = dry_data["STACKS"]["delete"] if "STACKS" in dry_data else None
    if deletable_vms or stopable_vms or skipped_vms:
        logger.info(
            f"VMs:\n\tDeletable: {deletable_vms}\n\tStoppable: {stopable_vms}\n\t"
            f"Skip: {skipped_vms}"
        )

    if deletable_discs:
        logger.info(f"DISCs:\n\tDeletable: {deletable_discs}")
    if deletable_nics:
        logger.info(f"NICs:\n\tDeletable: {deletable_nics}")
    if deletable_images:
        logger.info(f"IMAGES:\n\tDeletable: {deletable_images}")
    if deletable_pips:
        logger.info(f"PIPs:\n\tDeletable: {deletable_pips}")
    if deletable_ocps:
        logger.info(f"OCPs:\n\tDeletable: {deletable_ocps}")
    if deletable_resources:
        logger.info(f"RESOURCEs:\n\tDeletable: {deletable_resources}")
    if deletable_stacks:
        logger.info(f"STACKs:\n\tDeletable: {deletable_stacks}")
    if not any(
        [
            deletable_vms,
            stopable_vms,
            deletable_discs,
            deletable_nics,
            deletable_pips,
            deletable_resources,
            deletable_stacks,
            deletable_images,
        ]
    ):
        logger.info("\nNo resources are eligible for cleanup!")
    logger.info("\n====================================\n")


def total_running_time(vm_obj) -> namedtuple:
    """Calculates the VMs total running time

    :param ComputeResource.vm vm_obj: Instance of a VM from any compute resource
    :return: The total running time in seconds, minutes and hours
    """
    if vm_obj.creation_time is None:
        return None
    start_time = vm_obj.creation_time.astimezone(pytz.UTC)
    now_time = datetime.now().astimezone(pytz.UTC)
    timediff = now_time - start_time
    totalseconds = timediff.total_seconds()
    totalTime = namedtuple("TotalTime", ["seconds", "minutes", "hours"])
    return totalTime(seconds=totalseconds, minutes=totalseconds / 60, hours=totalseconds / 3600)


def gce_zones() -> list:
    """Returns the list of GCE zones"""
    _bcds = dict.fromkeys(["us-east1", "europe-west1"], ["b", "c", "d"])
    _abcfs = dict.fromkeys(["us-central1"], ["a", "b", "c", "f"])
    _abcs = dict.fromkeys(
        [
            "us-east4",
            "us-west1",
            "europe-west4",
            "europe-west3",
            "europe-west2",
            "asia-east1",
            "asia-southeast1",
            "asia-northeast1",
            "asia-south1",
            "australia-southeast1",
            "southamerica-east1",
            "asia-east2",
            "asia-northeast2",
            "europe-north1",
            "europe-west6",
            "northamerica-northeast1",
            "us-west2",
        ],
        ["a", "b", "c"],
    )
    _zones_combo = {**_bcds, **_abcfs, **_abcs}
    zones = [f"{loc}-{zone}" for loc, zones in _zones_combo.items() for zone in zones]
    return zones


def group_ocps_by_cluster(resources=None) -> dict:
    clusters_map = {}

    for resource in resources:
        for key in resource.get_tags(regex=OCP_TAG_SUBSTR):
            cluster_name = key.get("Key")
            if OCP_TAG_SUBSTR in cluster_name:
                cluster_name = cluster_name.split(OCP_TAG_SUBSTR)[1]
                if cluster_name not in clusters_map.keys():
                    clusters_map[cluster_name] = {"Resources": [], "Instances": []}

                # Set cluster's EC2 instances
                if hasattr(resource, 'ec2_instance'):
                    clusters_map[cluster_name]["Instances"].append(resource)
                # Set resource under cluster
                else:
                    clusters_map[cluster_name]["Resources"].append(resource)
    return clusters_map


def filter_resources_by_time_modified(
    resources: list[ResourceExplorerResource] = None, time_ref=""
) -> list:
    """
    Filter list of AWS resources by checking modification date ("LastReportedAt")

    :param list resources: List of resources to be filtered out
    :param str time_ref: a relative time reference for indicating the filter value
        of a relative time, given in a {time_value}{time_unit} format; default is "" (no filtering)


    :return: list of resources that last modified before time threshold

    :Example:
        Use the time_ref "1h" to collect resources that exist for more than an hour
    """
    filtered_resources = []
    if time_ref is None:
        time_ref = ""

    if time_ref.isnumeric():
        # Use default time value as Minutes
        time_ref += "m"

    # Time Ref is Optional; if empty, time_threshold will be set as "now"
    time_threshold = dateparser.parse(f"now-{time_ref}-UTC")

    for resource in resources:
        # Will not collect resources recorded during the SLA time
        if resource.date_modified > time_threshold:
            continue
        filtered_resources.append(resource)
    return filtered_resources


def delete_ocp(ocp):
    # WIP: add support for deletion
    pass
