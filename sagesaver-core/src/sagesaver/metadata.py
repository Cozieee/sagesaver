from collections import defaultdict

import boto3
from ec2_metadata import EC2Metadata
import jmespath


class MetadataPlus(EC2Metadata):
    def __init__(self):
        EC2Metadata.__init__(self)
        self.client = boto3.client('ec2', self.region)

    @property
    def tags(self):
        filters = [
            {
                'Name': 'resource-id',
                'Values': [self.instance_id]
            }
        ]

        response = self.client.describe_tags(Filters=filters)

        tags = jmespath.search('Tags', response)
        tags = defaultdict(
            lambda: None, {tag['Key']: tag['Value'] for tag in tags})

        return tags

metadata_plus = MetadataPlus()
