class SageSaverError(Exception):
    
    def __init__(self, **kwargs):
        msg = self.fmt.format(**kwargs)
        super().__init__(self, msg)

class UnconfiguredError(SageSaverError):

    fmt = 'CLI environmental variables have not been configured'

class ConfigurationForbiddenError(SageSaverError):

    fmt = 'Cannot configure type {entity_type}: {reason}'

class InstallationFailedError(SageSaverError):

    fmt = 'Installation of {entity_type} entity failed'

class InstallationRequiredError(SageSaverError):

    fmt = 'Installation of {entity_type} is required before {action}'