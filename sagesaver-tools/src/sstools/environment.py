import json
import boto3
import jmespath
from pymongo import MongoClient
from pymysql.connections import Connection

class Environment():
    def __init__(self, stack, region='us-west-2'):
        self.stack = stack
        self.session = boto3.session.Session(region_name=region)
        
    def notebooks_running(self):
        """List notebook servers currently running in a stack

        Returns:
            list(ec2 id): Stack notebook servers that are running
        """

        filters = [
            {
                "Name": "tag:sagesaver:stack-origin",
                "Values": [self.stack]
            },
            {
                "Name": "tag:sagesaver:server-type",
                "Values": ["Notebook"]
            },
            {
                "Name": "instance-state-name",
                "Values": ["running", "pending"]
            }
        ]

        client = self.session.client('ec2')
        response = client.describe_instances(Filters = filters)
        notebook_instances = jmespath.search("Reservations[].Instances[].InstanceId", response)

        return notebook_instances

    def db_secret(self):
        '''Retrieves SageSaver database credentials from Secrets Manager

        Returns:
            json: Database credentials
        '''

        client = self.session.client('secretsmanager')
        secret_name = f'{self.stack}-Database-Secret'
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
        secret = get_secret_value_response['SecretString']

        return json.loads(secret)

    def mongo_client(self):
        '''Generates a client to a SageSaver MongoDB database

        Returns:
            pymongo client: Client connected to the mongo database
        '''

        secret = self.db_secret()

        return MongoClient(
            username=secret['username'],
            password=secret['password'],
            port=secret['port'],
            host=secret['host']
        )

    def mysql_client(self):
        '''Generates a client to a SageSaver MySQL database

        Returns:
            pymysql client: Client connected to the mysql database
        '''

        secret = self.db_secret()

        return Connection(
            user=secret['username'],
            password=secret['password'],
            port=secret['port'],
            host=secret['host']
        )
