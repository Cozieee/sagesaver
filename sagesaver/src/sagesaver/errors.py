class SageSaverError(Exception):
    
    def __init__(self, **kwargs):
        msg = self.fmt.format(**kwargs)
        super().__init__(msg)

class EntryNotFoundError(SageSaverError):

    fmt = 'The requested entry or type could not be found'