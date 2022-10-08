import click

from cloudwash.config import settings
from cloudwash.config import validate_provider
from cloudwash.logger import logger
from cloudwash.providers.aws import cleanup as awsCleanup
from cloudwash.providers.azure import cleanup as azureCleanup
from cloudwash.providers.gce import cleanup as gceCleanup

# Adding the pythonpath for importing modules from cloudwash packages
# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))


# Common Click utils

_common_options = [
    click.option("--vms", is_flag=True, help="Remove only unused VMs from the provider"),
    click.option("--discs", is_flag=True, help="Remove only unused DISCs from the provider"),
    click.option("--nics", is_flag=True, help="Remove only unused NICs from the provider"),
    click.option(
        "--all",
        "_all",
        is_flag=True,
        help="Remove all unused Resources from the provider",
    ),
]


def common_options(func):
    for option in _common_options:
        func = option(func)
    return func


# Click Interactive for Cloud Resources Cleanup


@click.group(
    help="A Cleanup Utility to remove the VMs, Discs and Nics from Providers!",
    invoke_without_command=True,
)
@click.option("--version", is_flag=True, help="Get installed version of cloudwash in system")
@click.option("-d", "--dry", is_flag=True, help="Only show what will be removed from Providers!")
@click.pass_context
def cleanup_providers(ctx, dry, version):
    if version:
        import pkg_resources

        cloudwash_version = pkg_resources.get_distribution("cloudwash").version
        click.echo(f"Version: {cloudwash_version}")
        click.echo(f"Settings File: {settings.settings_file}")
    if ctx.invoked_subcommand:
        logger.info(
            f"\n<<<<<<< Running the cleanup script in {'DRY' if dry else 'ACTION'} RUN mode >>>>>>>"
        )


@cleanup_providers.command(help="Cleanup GCE provider")
@common_options
@click.pass_context
def gce(ctx, vms, discs, nics, _all):
    # Validate GCE Settings
    validate_provider(ctx.command.name)
    is_dry_run = ctx.parent.params["dry"]
    gceCleanup(vms=vms, discs=discs, nics=nics, _all=_all, dry_run=is_dry_run)


@cleanup_providers.command(help="Cleanup Azure provider")
@common_options
@click.option("--pips", is_flag=True, help="Remove only PiPs from the provider")
@click.option(
    "--all_rg",
    "_all_rg",
    is_flag=True,
    help="Remove resource group only if all resources are older than SLA",
)
@click.pass_context
def azure(ctx, vms, discs, nics, pips, _all, _all_rg):
    # Validate Azure Settings
    validate_provider(ctx.command.name)
    is_dry_run = ctx.parent.params["dry"]
    azureCleanup(
        vms=vms,
        discs=discs,
        nics=nics,
        pips=pips,
        _all=_all,
        _all_rg=_all_rg,
        dry_run=is_dry_run,
    )


@cleanup_providers.command(help="Cleanup Amazon provider")
@common_options
@click.option("--pips", is_flag=True, help="Remove only Public IPs from the provider")
@click.option("--stacks", is_flag=True, help="Remove only CloudFormations from the provider")
@click.pass_context
def aws(ctx, vms, discs, nics, pips, stacks, _all):
    # Validate Amazon Settings
    validate_provider(ctx.command.name)
    is_dry_run = ctx.parent.params["dry"]
    awsCleanup(
        vms=vms, discs=discs, nics=nics, pips=pips, stacks=stacks, _all=_all, dry_run=is_dry_run
    )


@cleanup_providers.command(help="Cleanup VMWare provider")
@common_options
@click.pass_context
def vmware(ctx, vms, discs, nics, _all):
    validate_provider(ctx.command.name)
    # TODO: Further TO_BE_IMPLEMENTED


@cleanup_providers.command(help="Cleanup RHEV provider")
@common_options
@click.pass_context
def rhev(ctx, vms, discs, nics, _all):
    validate_provider(ctx.command.name)
    # TODO: Further TO_BE_IMPLEMENTED


@cleanup_providers.command(help="Cleanup OSP provider")
@common_options
@click.pass_context
def openstack(ctx, vms, discs, nics, _all):
    validate_provider(ctx.command.name)
    # TODO: Further TO_BE_IMPLEMENTED


if __name__ == "__main__":
    cleanup_providers()
