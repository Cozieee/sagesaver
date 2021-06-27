import json
import boto3
from pymongo import MongoClient

from config import config

STACK_NAME = config["aws"]["stack"]

def get_secret(stack_name):
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=session.region_name
    )
    
    secret_name = f'{stack_name}-Database-Secret'
    get_secret_value_response = client.get_secret_value(SecretId=secret_name)
    secret = get_secret_value_response['SecretString']
    
    return json.loads(secret)

def get_mongo_client(stack_name):
    secret = get_secret(stack_name)

    db_username = secret['username']
    db_password = secret['password']
    db_port = secret['port']
    db_host = secret['host']

    uri_str = f"mongodb://{db_username}:{db_password}@{db_host}:{db_port}"
    return MongoClient(uri_str)

client = get_mongo_client(STACK_NAME)