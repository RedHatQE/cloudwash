"""Common utils for cleanup activities of all CRs"""
import importlib.resources
from collections import namedtuple
from datetime import datetime

import dateparser
import dominate
import pytz
from dominate.tags import br
from dominate.tags import caption
from dominate.tags import div
from dominate.tags import h1
from dominate.tags import style
from dominate.tags import table
from dominate.tags import tbody
from dominate.tags import td
from dominate.tags import tr
from dominate.util import raw
from wrapanapi.systems.ec2 import ResourceExplorerResource

from cloudwash.assets import css
from cloudwash.logger import logger

OCP_TAG_SUBSTR = "kubernetes.io/cluster/"

_vms_dict = {"VMS": {"delete": [], "stop": [], "skip": []}}
_containers_dict = {"CONTAINERS": {"delete": [], "stop": [], "skip": []}}

dry_data = {
    "NICS": {"delete": []},
    "DISCS": {"delete": []},
    "PIPS": {"delete": []},
    "OCPS": {"delete": []},
    "RESOURCES": {"delete": []},
    "STACKS": {"delete": []},
    "IMAGES": {"delete": []},
    "PROVIDER": "",
    "REGION": "",
    "GROUP": "",
    "ZONE": "",
}
non_rt_keys = ('provider', 'zone', 'region', 'group')

dry_data.update(_vms_dict)
dry_data.update(_containers_dict)


def resourcewise_data(dry_data=None) -> dict:
    resource_data = {
        "provider": dry_data.get('PROVIDER'),
        "region": dry_data.get('REGION'),
        "group": dry_data.get('GROUP'),
        "zone": dry_data.get('ZONE'),
        "deletable_vms": dry_data["VMS"]["delete"],
        "stopable_vms": dry_data["VMS"]["stop"],
        "skipped_vms": dry_data["VMS"]["skip"],
        "deletable_containers": dry_data["CONTAINERS"]["delete"],
        "stopable_containers": dry_data["CONTAINERS"]["stop"],
        "skipped_containers": dry_data["CONTAINERS"]["skip"],
        "deletable_discs": dry_data["DISCS"]["delete"],
        "deletable_nics": dry_data["NICS"]["delete"],
        "deletable_images": dry_data["IMAGES"]["delete"],
        "deletable_pips": dry_data["PIPS"]["delete"] if "PIPS" in dry_data else None,
        "deletable_resources": dry_data["RESOURCES"]["delete"],
        "deletable_stacks": dry_data["STACKS"]["delete"] if "STACKS" in dry_data else None,
        "deletable_ocps": {
            ocp.resource_type: [
                r.name for r in dry_data["OCPS"]["delete"] if r.resource_type == ocp.resource_type
            ]
            for ocp in dry_data["OCPS"]["delete"]
        },
    }
    return resource_data


def echo_dry(dry_data=None) -> None:
    """Prints and Logs the per resource cleanup data on STDOUT and logfile

    :param dict dry_data: The deletable resources dry data of a Compute Resource,
        it follows the format of module scoped `dry_data` variable in this module
    """
    logger.info("\n=========== DRY SUMMARY ============\n")

    # Group the same resource type under the same section for logging
    grouped_resources = {}
    resource_data = resourcewise_data(dry_data)
    for key, value in resource_data.items():
        if key not in non_rt_keys and value:
            suffix = key.split('_')[1].upper()
            action = key.split('_')[0].title()

            if suffix not in grouped_resources.keys():
                grouped_resources[suffix] = {}
            grouped_resources[suffix][action] = value

    if any(value for key, value in resource_data.items() if key not in non_rt_keys):
        for suffix, actions in grouped_resources.items():
            logger.info(f"{suffix}:")
            for action, value in actions.items():
                logger.info(f"\t{action}: {value}")
    else:
        logger.info("\nNo resources are eligible for cleanup!\n")

    logger.info("\n====================================\n")


def table_caption(kwargs):
    '''Returns the caption for the table based on the provider'''
    caption_dict = {
        'GCE': f"Zone: {kwargs.get('zone')}",
        'AZURE': f"Region: {kwargs.get('region')}, Group: {kwargs.get('group')}",
        'AWS': f"Region: {kwargs.get('region')}",
    }
    provider = kwargs.get('provider')
    return caption_dict.get(provider, '')


def create_html(provider, all_data):
    """
    Creates an HTML report file with deletable resources for a given provider.
    Args:
        provider (str): The name of the cloud provider.
        all_data (list): A list of dictionaries containing resource data for different regions.
    Returns:
        None: The function writes the generated HTML content to
        a file named 'cleanup_resource_<provider>.html'.
    The generated HTML report includes:
        - A title "Cloud resources page".
        - A header "CLOUDWASH REPORT-<provider>".
        - A table for each region's resource data.
        - Resource names listed with bullet points.
        - Nested resource types and their respective resources.
    Note:
        The function uses the 'dominate' library to create the HTML structure and
        'importlib.resources' to read a CSS file for styling.
    """
    doc = dominate.document(title="Cloud resources page")
    with doc.head:
        with importlib.resources.open_text(css, 'reporting.css') as css_file:
            style(css_file.read())
    with doc:
        with div(cls='cloud_box'):
            h1(f'CLOUDWASH REPORT - {provider}')
            for region_data in all_data:
                data = resourcewise_data(region_data)
                # Check if there is any data to display, else skip creating the table
                if any(data[key] for key in data.keys() if key not in non_rt_keys):
                    with table(id='cloud_table'):
                        tab_caption = table_caption(data)
                        caption(tab_caption)
                        with tbody():
                            for table_head in data.keys():
                                if data[table_head] and table_head not in non_rt_keys:
                                    with tr():
                                        td(table_head.replace("_", " ").title())
                                        bullet = '&#8226;'
                                        tab = '&nbsp;'
                                        if isinstance(data[table_head], list):
                                            component = ''
                                            for resource_name in data[table_head]:
                                                component += bullet + ' ' + resource_name + ' '
                                            td(raw(component))
                                        elif isinstance(data[table_head], dict):
                                            component = []
                                            for rtype, resources in data[table_head].items():
                                                comp_line = ' ' + tab * 2 + ' '
                                                rtype_line = bullet + rtype + str(br())
                                                for resource_name in resources:
                                                    comp_line += bullet + ' ' + resource_name + ' '
                                                component.append(rtype_line + comp_line)
                                            td(raw(str(br()).join(component)))
                                        else:
                                            td(raw(bullet + ' ' + data[table_head]))
    with open(f'cleanup_resource_{provider}.html', 'w') as file:
        file.write(doc.render())


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


def group_ocps_by_cluster(resources: list = None) -> dict:
    """Group different types of AWS resources under their original OCP clusters

    :param list resources: AWS resources collected by defined region and sla
    :return: A dictionary with the clusters as keys and the associated resources as values
    """
    if resources is None:
        resources = []
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


def calculate_time_threshold(time_ref=""):
    """Parses a time reference for data filtering

    :param str time_ref: a relative time reference for indicating the filter value
    of a relative time, given in a {time_value}{time_unit} format; default is "" (no filtering)
    :return datetime time_threshold
    """
    if time_ref is None:
        time_ref = ""

    if time_ref.isnumeric():
        # Use default time value as Minutes
        time_ref += "m"

    # Time Ref is Optional; if empty, time_threshold will be set as "now"
    time_threshold = dateparser.parse(f"now-{time_ref}-UTC")
    logger.debug(
        f"\nAssociated OCP resources are filtered by last creation time of: {time_threshold}"
    )
    return time_threshold


def filter_resources_by_time_modified(
    time_threshold,
    resources: list[ResourceExplorerResource] = None,
) -> list:
    """
    Filter list of AWS resources by checking modification date ("LastReportedAt")
    :param datetime time_threshold: Time filtering criteria
    :param list resources: List of resources to be filtered out
    :return: list of resources that last modified before time threshold

    :Example:
        Use the time_ref "1h" to collect resources that exist for more than an hour
    """
    filtered_resources = []

    for resource in resources:
        # Will not collect resources recorded during the SLA time
        if resource.date_modified > time_threshold:
            continue
        filtered_resources.append(resource)
    return filtered_resources


def delete_ocp(ocp):
    # WIP: add support for deletion
    pass
