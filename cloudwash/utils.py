'''Common utils for cleanup activities of all CRs'''

from collections import namedtuple
from datetime import datetime
from cloudwash.logger import logger
import pytz

_vms_dict = {'VMS': {'delete': [], 'stop': []}}
dry_data = {'NICS': {'delete': []}, 'DISCS': {'delete': []}, 'PIPS': {'delete': []}}
dry_data.update(_vms_dict)


def echo_dry(dry_data=None) -> None:
    """Prints and Logs the per resource cleanup data on STDOUT and logfile

    :param dict dry_data: The deletable resources dry data of a Compute Resource,
        it follows the format of module scoped `dry_data` variable in this module
    """
    logger.info('\n=========== DRY SUMMARY ============\n')
    deletable_vms = dry_data['VMS']['delete']
    stopable_vms = dry_data['VMS']['stop']
    deletable_discs = dry_data["DISCS"]['delete']
    deletable_nics = dry_data["NICS"]['delete']
    deletable_pips = dry_data["PIPS"]['delete'] if 'PIPS' in dry_data else None

    if deletable_vms or stopable_vms:
        logger.info(f'VMs:\n\tDeletable: {deletable_vms}\n\tStoppable: {stopable_vms}')
    if deletable_discs:
        logger.info(f'DISCs:\n\tDeletable: {deletable_discs}')
    if deletable_nics:
        logger.info(f'NICs:\n\tDeletable: {deletable_nics}')
    if deletable_pips:
        logger.info(f'PIPs:\n\tDeletable: {deletable_pips}')
    if not any([deletable_vms, stopable_vms, deletable_discs, deletable_nics, deletable_pips]):
        logger.info('No resources are eligible for cleanup!')
    logger.info('\n====================================\n')


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
    totalTime = namedtuple('TotalTime', ['seconds', 'minutes', 'hours'])
    return totalTime(seconds=totalseconds, minutes=totalseconds / 60, hours=totalseconds / 3600)


def gce_zones() -> list:
    """Returns the list of GCE zones"""
    _bcds = dict.fromkeys(['us-east1', 'europe-west1'], ['b', 'c', 'd'])
    _abcfs = dict.fromkeys(['us-central1'], ['a', 'b', 'c', 'f'])
    _abcs = dict.fromkeys(
        [
            'us-east4',
            'us-west1',
            'europe-west4',
            'europe-west3',
            'europe-west2',
            'asia-east1',
            'asia-southeast1',
            'asia-northeast1',
            'asia-south1',
            'australia-southeast1',
            'southamerica-east1',
            'asia-east2',
            'asia-northeast2',
            'europe-north1',
            'europe-west6',
            'northamerica-northeast1',
            'us-west2',
        ],
        ['a', 'b', 'c'],
    )
    _zones_combo = {**_bcds, **_abcfs, **_abcs}
    zones = [f'{loc}-{zone}' for loc, zones in _zones_combo.items() for zone in zones]
    return zones
