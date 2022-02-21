from dynaconf import Dynaconf
from dynaconf import Validator
from cloudwash.logger import logger

# Initialize and Configure Settings
settings = Dynaconf(envvar_prefix="CLEANUP", settings_file='settings.yaml')


def validate_provider(provider_name):
    provider = provider_name.upper()
    provider_settings = [f'{provider}.{setting_key}' for setting_key in settings.to_dict()['PROVIDERS'].get(provider)]
    settings.validators.register(Validator(*provider_settings, ne=None))
    try:
        settings.validators.validate()
        logger.info(f'The {provider} providers settings are initialized and validated !')
    except Exception:
        raise
