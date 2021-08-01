from copy import deepcopy
from enum import Enum
import json

from sagesaver.exceptions import (
    ConfigurationForbiddenError,
    InstallationFailedError,
    InstallationRequiredError
)
from .cliconfig import ConfigManager
from .entitytypes import EntityTypes

class EntityConfiguration():

    def __init__(self, new_type, stack_name, region):

        self.manager = ConfigManager()

        if type not in EntityTypes:
            raise ConfigurationForbiddenError(
                type, f'{new_type} is not a supported Entity Type'
            )

        self.entity_type = EntityTypes[new_type]

        current_type = self.manager.config['environmental']['type']

        if current_type not in ['USER', None]:
            raise ConfigurationForbiddenError(
                type, f'{current_type} does not support reconfiguration'
            )

        self.installation = self.entity_type.installation
        self.installed = self.installation is not None

        self.stack_name = stack_name
        self.region = region

    def install(self, *args, **kwargs):
        try:
            self.installation(*args, **kwargs)
        except:
            raise InstallationFailedError(self.entity_type)
        
        self.installed = True

    def configure_environmentals(self):
        if not self.installed:
            raise InstallationRequiredError(
                entity_type = self.entity_type, 
                action='configuring cli environmental vars'
            )
        
        self.manager.config.update('environmental', {
            'type': self.entity_type,
            'stack_name': self.stack_name,
            'region': self.region
        })
