import json
import boto3
from pymongo import MongoClient

from config import config

STACK_NAME = config["aws"]["stack"]
AWS_REGION = config["aws"]["region"]

def get_database_secret(client, stack):
    '''Retrieves SageSaver database credentials from Secrets Manager

    Args:
        client (boto3 service client): Secrets Manager service client
            used for credential retrieval
        stack (string): Name of the SageSaver Environment Stack housing
             the database
    
    Returns:
        json: Database credentials
    '''

    secret_name = f'{stack}-Database-Secret'
    get_secret_value_response = client.get_secret_value(SecretId=secret_name)
    secret = get_secret_value_response['SecretString']

    return json.loads(secret)

def get_mongo_client(session, stack):
    '''Generates a mongo client to the SageSaver MongoDB database

    Args:
        session (boto3 session): Session used to generate a
            Secrets Manager client
        stack (string): Name of the SageSaver Environment Stack housing
            the database
    
    Returns:
        pymongo client: Client connected to the SageSaver database
    '''

    secrets_client = session.client('secretsmanager')
    secret = get_database_secret(secrets_client, stack)

    db_username = secret['username']
    db_password = secret['password']
    db_port = secret['port']
    db_host = secret['host']

    return MongoClient(
        username=db_username,
        password=db_password,
        port=db_port,
        host=db_host
    )

aws_session = boto3.session.Session(region_name = AWS_REGION)
client = get_mongo_client(aws_session, STACK_NAME)