import json
import os

from .interface import Interface

# TODO Describe Tags Permission
# TODO Cloudformation read output
# TODO Give Server templates a Database Secret Name Tag & remove sagesaver:


class Server(Interface):
    '''
    required tags: stack-origin, database-secret-name
    '''

    def __init__(self, time_limit, **kwargs):
        self.time_limit = time_limit
        super().__init__(**kwargs)

    @property
    def idle(self):
        return False

    def autostop(self):
        if self.idle:
            os.system('sudo shutdown now -h')

    def get_secret(self, secret_name):
        client = self.session.client('secretsmanager')

        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name)
        secret = get_secret_value_response['SecretString']

        return json.loads(secret)
