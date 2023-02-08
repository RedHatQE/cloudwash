from contextlib import contextmanager


@contextmanager
def compute_client(compute_resource, client=None):
    """The context manager for compute resource client to initiate and disconnect
    :param str compute_resource: The compute resource name
    :param obj client: Client object
    """
    supported_providers = ["azure", "gce", "aws"]
    if compute_resource in supported_providers:
        client = client
    else:
        raise ValueError(
            f"{compute_resource} is an incorrect value. It should be one of {supported_providers}"
        )
    try:
        yield client
    finally:
        client.disconnect()
