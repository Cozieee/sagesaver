import boto3
import jmespath
import json
from pymongo import MongoClient
from werkzeug.utils import cached_property
from configparser import ConfigParser

from sagesaver.metadata import metadata_plus as mp

# TODO Describe Tags Permission
# TODO Cloudformation read output
# TODO Give Server templates a Database Secret Name Tag & remove sagesaver:

class Server():
    region = mp.region
    server_type = mp.tags['server-type']
    
    def __init__(self, conf_path = '/etc/sagesaver.conf'):
        self.conf_path = conf_path
        
        self.session = boto3.session.Session(region_name=self.region)
        
        self.conf = ConfigParser()
        self.conf.read(conf_path)
    
    def get_secret(self, secret_name):
        client = self.session.client('secretsmanager')
        
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
        secret = get_secret_value_response['SecretString']

        return json.loads(secret)

    @cached_property
    def origin_stack(self):
        client = self.session.client('cloudformation')
        
        response = client.describe_stacks(StackName=mp.tags['stack-origin'])
        stack = jmespath.search('Stacks[0]', response)
        
        return stack
    
    def origin_output(self, key):
        return jmespath.search(f"Outputs[?OutputKey=='{key}'] | [0].OutputValue", self.origin_stack)
        
    @cached_property
    def db_type(self):
        return self.origin_output('DBType')
    
    @cached_property
    def db_secret(self):
        secret_name = mp.tags['database-secret-name']
        return self.get_secret(secret_name)
    
    def db_client(self):
        secret  = self.db_secret
        
        if self.db_type == 'mongo':
            return MongoClient(
                username=secret['username'],
                password=secret['password'],
                port=secret['port'],
                host=secret['host']
            )
        elif self.db_type == 'mysql':
            return Connection(
                user=secret['username'],
                password=secret['password'],
                port=secret['port'],
                host=secret['host']
            )
        else:
            return None
    
    def autostop(self):
        pass
        
    @classmethod
    def create(self):
        from .notebook import Notebook
        from .database import Mongo, Mysql

        server_type = self.server_type

        if server_type == 'notebook':
            return Notebook()
        elif server_type == 'database':
            db_type = self.db_type

            if db_type == 'mongo':
                return Mongo()
            elif db_type == 'mysql':
                return Mysql()

        return None