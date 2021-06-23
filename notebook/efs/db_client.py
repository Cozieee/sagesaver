import os
from dotenv import load_dotenv

def get_secret(stack_name):
    import boto3

    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=session.region_name
    )
    
    secret_name = f'{stack_name}-DBSecret'
    get_secret_value_response = client.get_secret_value(SecretId=secret_name)
    secret = get_secret_value_response['SecretString']
    
    return json.loads(secret)

def get_client(stack_name):
    secret = get_secret(stack_name)

    db_username = secret['username']
    db_password = secret['password']
    db_port = secret['port']
    db_host = secret['host']

    uri_str = f"mongodb://{db_username}:{db_password}@{db_host}:{db_port}"
    return MongoClient(uri_str)

load_dotenv()
ENV_STACK_NAME = os.getenv('ENV_STACK_NAME') 

client = get_client(ENV_STACK_NAME)