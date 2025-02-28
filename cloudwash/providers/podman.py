"""PODMAN CR Cleanup Utilities"""
from copy import deepcopy

from cloudwash.client import compute_client
from cloudwash.constants import container_data as data
from cloudwash.entities.providers import PodmanCleanup
from cloudwash.utils import create_html
from cloudwash.utils import dry_data
from cloudwash.utils import echo_dry


def cleanup(**kwargs):
    is_dry_run = kwargs.get("dry_run", False)
    dry_data['PROVIDER'] = "PODMAN"
    all_data = []
    for items in data:
        dry_data[items]['delete'] = []
    with compute_client("podman") as podman_client:
        podmancleanup = PodmanCleanup(client=podman_client)
        # Actual Cleaning and dry execution
        if kwargs["containers"]:
            podmancleanup.containers.cleanup()
        if is_dry_run:
            echo_dry(dry_data)
            all_data.append(deepcopy(dry_data))
    if is_dry_run:
        create_html(dry_data['PROVIDER'], all_data)
