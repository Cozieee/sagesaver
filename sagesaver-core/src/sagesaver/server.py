import json
import os

import boto3
from cached_property import cached_property
from pymongo import MongoClient
from pymysql.connections import Connection

from .metadata import metadata_plus as mp
from .environment import environment as env

# TODO Describe Tags Permission
# TODO Cloudformation read output
# TODO Give Server templates a Database Secret Name Tag & remove sagesaver:

class Server():
    '''
    required tags: stack-origin, database-secret-name
    '''
    session = boto3.session.Session(region_name=mp.region)

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

    @cached_property
    def db_secret(self):
        secret_name = mp.tags['database-secret-name']
        return self.get_secret(secret_name)

    def db_client(self):
        secret = self.db_secret
        db_type = env.output('DBType')

        if db_type == 'mongo':
            return MongoClient(
                username=secret['username'],
                password=secret['password'],
                port=secret['port'],
                host=secret['host']
            )
        elif db_type == 'mysql':
            return Connection(
                user=secret['username'],
                password=secret['password'],
                port=secret['port'],
                host=secret['host']
            )
        else:
            return None

    @classmethod
    def get_server_class(self):
        server_type = mp.tags['server-type']

        if server_type == 'notebook':
            return 'notebook'
        elif server_type == 'database':
            return mp.tags['database-type']