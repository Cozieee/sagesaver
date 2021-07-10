import boto3
from cached_property import cached_property
import jmespath

from .metadata import metadata_plus as mp

class Environment():

    def __init__(self):
        self.session = boto3.session.Session(region_name=mp.region)

    @cached_property
    def stack(self):
        client = self.session.client('cloudformation')

        response = client.describe_stacks(StackName=mp.tags['stack-origin'])
        stack = jmespath.search('Stacks[0]', response)

        return stack
    
    def output(self, key):
        return jmespath.search(f"Outputs[?OutputKey=='{key}'] | [0].OutputValue", self.stack)

environment = Environment()