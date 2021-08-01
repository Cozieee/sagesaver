import boto3

class Environmental():

    def __init__(self, stack_name, region):
        self.stack_name = stack_name
        self.session = boto3.session.Session(region_name=region)