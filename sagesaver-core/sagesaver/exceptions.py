class SageSaverError(Exception):
    
    def __init__(self, **kwargs):
        msg = self.fmt.format(**kwargs)
        super().__init__(self, msg)

class UnconfiguredError(SageSaverError):

    fmt = 'CLI environmental variables have not been configured'

class ReconfigureForbiddenError(SageSaverError):

    fmt = 'Cannot reconfigure {old_type} into {new_type}'