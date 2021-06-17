import os
import boto3
from botocore.exceptions import ClientError

from config import config

aws = config["aws"]
ec2 = boto3.client('ec2', aws["region"])

try:
    ec2.start_instances(InstanceIds = [aws["db-id"]])
except ClientError:
    msg = "Shutting down... Mongo Server is in stopping state and cannot be started. Start this instance again when Mongo Server has stopped"
    os.system(f'sudo shutdown now -h "{msg}"')
