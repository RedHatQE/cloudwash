"""PODMAN CR Cleanup Utilities"""
from cloudwash.client import compute_client
from cloudwash.constants import container_data as data
from cloudwash.entities.providers import PodmanCleanup
from cloudwash.utils import create_html
from cloudwash.utils import DryData
from cloudwash.utils import print_dry_data


def cleanup(**kwargs):
    is_dry_run = kwargs.get("dry_run", False)
    dry_data = DryData()
    dry_data['PROVIDER'] = "PODMAN"
    all_data = []
    for items in data:
        dry_data.reset_resource(items)
    with compute_client("podman") as podman_client:
        podmancleanup = PodmanCleanup(client=podman_client, dry_data=dry_data)
        # Actual Cleaning and dry execution
        if kwargs["containers"]:
            podmancleanup.containers.cleanup()
        print_dry_data(dry_data, is_dry_run, all_data)
    if is_dry_run:
        create_html(dry_data['PROVIDER'], all_data)
