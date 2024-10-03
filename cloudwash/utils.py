"""Common utils for cleanup activities of all CRs"""
from collections import namedtuple
from datetime import datetime

import dominate
import pytz
from dominate.tags import div
from dominate.tags import h1
from dominate.tags import h3
from dominate.tags import style
from dominate.tags import table
from dominate.tags import tbody
from dominate.tags import td
from dominate.tags import tr
from dominate.util import raw

from cloudwash.logger import logger


_vms_dict = {"VMS": {"delete": [], "stop": [], "skip": []}}
dry_data = {
    "NICS": {"delete": []},
    "DISCS": {"delete": []},
    "PIPS": {"delete": []},
    "RESOURCES": {"delete": []},
    "STACKS": {"delete": []},
    "IMAGES": {"delete": []},
    "PROVIDER": "",
}
dry_data.update(_vms_dict)


def echo_dry(dry_data=None) -> None:
    """Prints and Logs the per resource cleanup data on STDOUT and logfile

    :param dict dry_data: The deletable resources dry data of a Compute Resource,
        it follows the format of module scoped `dry_data` variable in this module
    """

    logger.info("\n=========== DRY SUMMARY ============\n")
    resource_data = {
        "provider": dry_data.get('PROVIDER'),
        "deletable_vms": dry_data["VMS"]["delete"],
        "stopable_vms": dry_data["VMS"]["stop"],
        "skipped_vms": dry_data["VMS"]["skip"],
        "deletable_discs": dry_data["DISCS"]["delete"],
        "deletable_nics": dry_data["NICS"]["delete"],
        "deletable_images": dry_data["IMAGES"]["delete"],
        "deletable_pips": dry_data["PIPS"]["delete"] if "PIPS" in dry_data else None,
        "deletable_resources": dry_data["RESOURCES"]["delete"],
        "deletable_stacks": dry_data["STACKS"]["delete"] if "STACKS" in dry_data else None,
    }

    # Group the same resource type under the same section for logging
    grouped_resources = {}
    for key, value in resource_data.items():
        if key != 'provider' and value:
            suffix = key.split('_')[1].upper()
            action = key.split('_')[0].title()

            if suffix not in grouped_resources.keys():
                grouped_resources[suffix] = {}
            grouped_resources[suffix][action] = value

    if any(value for key, value in resource_data.items() if key != 'provider'):
        for suffix, actions in grouped_resources.items():
            logger.info(f"{suffix}:")
            for action, value in actions.items():
                logger.info(f"\t{action}: {value}")
        logger.info("\n====================================\n")

        create_html(**resource_data)
    else:
        logger.info("\nNo resources are eligible for cleanup!\n")


def create_html(**kwargs):
    '''Creates a html based report file with deletable resources.'''
    doc = dominate.document(title="Cloud resources page")

    with doc.head:
        with open('assets/css/reporting.css', 'r') as css:
            style(css.read())

    with doc:
        with div(cls='cloud_box'):
            h1('CLOUDWASH REPORT')
            h3(f"{kwargs.get('provider')} RESOURCES")
            with table(id='cloud_table'):
                with tbody():
                    for table_head in kwargs.keys():
                        if kwargs[table_head] and table_head != "provider":
                            with tr():
                                td(table_head.replace("_", " ").title())
                                bullet = '&#8226;'
                                if isinstance(kwargs[table_head], list):
                                    component = ''
                                    for resource_name in kwargs[table_head]:
                                        component += bullet + ' ' + resource_name + ' '
                                    td(raw(component))
                                else:
                                    td(raw(bullet + ' ' + kwargs[table_head]))
    with open('cleanup_resource_{}.html'.format(kwargs.get('provider')), 'w') as file:
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
