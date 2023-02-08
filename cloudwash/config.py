import logging
from pathlib import Path
from pathlib import PurePath

from dynaconf import Dynaconf
from dynaconf import Validator

from cloudwash.logger import logger

CURRENT_DIRECTORY = Path().resolve()
settings_file = PurePath(CURRENT_DIRECTORY, 'settings.yaml')
# Initialize and Configure Settings
settings = Dynaconf(
    core_loaders=["YAML"],
    envvar_prefix="CLEANUP",
    settings_file=settings_file,
    preload=["conf/*.yaml"],
    envless_mode=True,
    lowercase_read=True,
)


def validate_provider(provider_name):
    provider = provider_name.upper()
    provider_settings = settings.to_dict().get(provider)
    if not provider_settings:
        logging.error("No provider settings found! Please check settings file!")
        exit()
    for account in provider_settings:
        account_settings = [f"{account}.{account_key}" for account_key in provider_settings]
        settings.validators.register(Validator(*account_settings, ne=None))
        try:
            settings.validators.validate()
            logger.info(
                f"The {provider} provider settings for account {account['NAME']}"
                f" are initialized and validated!"
            )
        except Exception as e:
            logging.error(f"Settings validation failed for {provider} account {account['NAME']}")
            raise e
