import os
import boto3
from botocore.exceptions import ClientError

from config import config

AWS_REGION = config["aws"]["region"]
DB_ID = config["aws"]["db-id"]

ec2 = boto3.client('ec2', AWS_REGION)

try:
    ec2.start_instances(InstanceIds = [DB_ID])
except ClientError:
    msg = "Shutting down... Mongo Server is in stopping state and cannot be started. Start this instance again when Mongo Server has stopped"
    os.system(f'sudo shutdown now -h "{msg}"')
