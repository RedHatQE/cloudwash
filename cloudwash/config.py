from pathlib import Path
from pathlib import PurePath

from dynaconf import Dynaconf
from dynaconf import Validator

from cloudwash.logger import logger

def generate_settings(settings_path):
    if settings_path==None:
        print("No settings file path specified using current directory as default.")
        CURRENT_DIRECTORY = Path().resolve()
        settings_file = PurePath(CURRENT_DIRECTORY, 'settings.yaml')
    else:
        settings_file = PurePath(settings_path)

    # Initialize and Configure Settings
    settings = Dynaconf(
        core_loaders=["YAML"],
        envvar_prefix="CLEANUP",
        settings_file=settings_file,
        preload=["conf/*.yaml"],
        envless_mode=True,
        lowercase_read=True,
    )
    return settings


def validate_provider(provider_name, settings):
    provider = provider_name.upper()
    provider_settings = [
        f"{provider}.{setting_key}" for setting_key in settings.to_dict().get(provider)
    ]
    settings.validators.register(Validator(*provider_settings, ne=None))
    try:
        settings.validators.validate()
        logger.info(f"The {provider} providers settings are initialized and validated !")
    except Exception:
        raise
