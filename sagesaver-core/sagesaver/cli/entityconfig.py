from sagesaver.exceptions import (
    ConfigurationForbiddenError,
    InstallationFailedError,
    InstallationRequiredError
)
from .cliconfig import ConfigManager
from .entitytypes import EntityTypes

class EntityConfiguration():

    reconfigurable_types = [
        EntityTypes.USER,
        EntityTypes.SEED
    ]

    def __init__(self, entity_type: str, stack_name: str, region: str):

        entity_type = entity_type.upper()

        self.manager = ConfigManager()

        try:
            self.entity_type = EntityTypes[entity_type]
        except KeyError:
            raise ConfigurationForbiddenError(
                entity_type = entity_type, 
                reason = 'not a supported Entity Type'
            )
        
        current_type = self.manager.config['environmental']['type']
        current_type = EntityTypes[current_type]

        if current_type not in self.reconfigurable_types:
            raise ConfigurationForbiddenError(
                entity_type = entity_type, 
                reason = f'{current_type} type (current) does not support reconfiguration'
            )

        self.installation = self.entity_type.installation
        self.installed = self.installation is None

        self.stack_name = stack_name
        self.region = region

    def install(self, *args, **kwargs):
        try:
            self.installation(*args, **kwargs)
        except:
            raise InstallationFailedError(
                entity_type = self.entity_type
            )
        
        self.installed = True

    def save_environmentals(self):
        if not self.installed:
            raise InstallationRequiredError(
                entity_type = self.entity_type, 
                action='saving cli environmental vars'
            )
        
        self.manager.update('environmental', {
            'type': self.entity_type.name,
            'stack_name': self.stack_name,
            'region': self.region
        })
