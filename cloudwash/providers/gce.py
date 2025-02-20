"""GCE CR Cleanup Utilities"""
from copy import deepcopy

from cloudwash.client import compute_client
from cloudwash.config import settings
from cloudwash.constants import gce_data as data
from cloudwash.entities.providers import GCECleanup
from cloudwash.logger import logger
from cloudwash.utils import create_html
from cloudwash.utils import dry_data
from cloudwash.utils import echo_dry
from cloudwash.utils import gce_zones


def cleanup(**kwargs):
    is_dry_run = kwargs.get("dry_run", False)
    dry_data['PROVIDER'] = "GCE"
    zones = settings.gce.auth.get('zones', ['all'])
    all_data = []

    if "all" in zones:
        zones = gce_zones()
    if kwargs["nics"] or kwargs["_all"]:
        logger.warning("Cloudwash does not supports NICs operation for GCE yet!")
    if kwargs["discs"] or kwargs["_all"]:
        logger.warning("Cloudwash does not supports DISCs operation for GCE yet!")

    with compute_client("gce") as gce_client:
        for zone in zones:
            dry_data['ZONE'] = zone
            for items in data:
                dry_data[items]['delete'] = []
            gce_client.cleaning_zone = zone
            gcecleanup = GCECleanup(client=gce_client)
            logger.info(f"\nResources from the zone: {zone}")
            if kwargs["vms"] or kwargs["_all"]:
                gcecleanup.vms.cleanup()
            if is_dry_run:
                echo_dry(dry_data)
                all_data.append(deepcopy(dry_data))

    if is_dry_run:
        create_html(dry_data['PROVIDER'], all_data)
