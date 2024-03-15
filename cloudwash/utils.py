"""Common utils for cleanup activities of all CRs"""
from collections import namedtuple
from datetime import datetime

import pytz

from cloudwash.logger import logger
import dominate
from dominate.tags import * 
_vms_dict = {"VMS": {"delete": [], "stop": [], "skip": []}}
dry_data = {
    "NICS": {"delete": []},
    "DISCS": {"delete": []},
    "PIPS": {"delete": []},
    "RESOURCES": {"delete": []},
    "STACKS": {"delete": []},
    "IMAGES": {"delete": []},
    "PROVIDER": ""
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
    create_html(provider=dry_data.get('PROVIDER'),deletable_vms=deletable_vms,stopable_vms=stopable_vms,skipped_vms=skipped_vms,deletable_discs=deletable_discs,deletable_nics=deletable_nics,deletable_pips=deletable_pips,deletable_resources=deletable_resources,deletable_stacks=deletable_stacks,deletable_images=deletable_images)

def create_html(**kwargs):
    doc = dominate.document(title="Cloud resources page")
    doc = add_css_style(doc=doc)
    with doc:
        with div(cls='cloud_box'):
            with table(id='cloud_table'):
                caption(h3(f"{kwargs.get('provider')} RESOURCES"))
                with thead():
                    with tr():
                        for table_head in kwargs.keys():
                            if kwargs[table_head] and table_head!="provider":
                                th(table_head.replace("_"," ").title())
                with tbody():
                    for key,values in kwargs.items():
                        if key!="provider" and values:
                            with td():
                                if isinstance(values,list):
                                    with ul():
                                        [li(resource_name) for resource_name in values]
                                else:
                                    td(values)
    with open('index.html','a') as file:
            file.write(doc.render())
            
def add_css_style(doc):
    with doc.head:
        style('''
            table, th, td {
                border-collapse: collapse;
                margin-left: auto;
                margin-right: auto;
            }

            #cloud_table {
                border-collapse: collapse;
                margin: 25px auto;
                font: 0.9em sans-serif;
                min-width: 800px;
                box-shadow: 0 0 20px rgba(0, 0, 0, 0.15);
                border-radius: 5px 5px 0 0;
                overflow: hidden;
            }

            #cloud_table thead tr {
                background-color: #009879;
                color: #ffffff;
                text-align: center;
                font-weight: bold;
            }

            #cloud_table th, #cloud_table td {
                padding: 12px 15px;
            }

            #cloud_table th:not(:last-child), #cloud_table td:not(:last-child) {
                border-right: 0.1px solid black;
            }

            #cloud_table tbody tr {
                border-bottom: 1px solid #dddddd;
                color: #009999;
                font-weight: bold;
            }

            #cloud_table tbody tr:nth-of-type(odd) {
                background-color: #f3f3f3;
            }

            #cloud_table tbody tr:last-of-type {
                border-bottom: 2px solid #009879;
            }

            #cloud_table tbody td {
                text-align: left;
            }

            ul {
                margin: 0;
                padding: 0 0 0 20px;
                list-style-type: circle;
            }

            ul li {
                margin-top: 10px;
                margin-bottom: 10px;
            }
        ''')
    return doc

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
