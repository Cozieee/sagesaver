from boto3 import Session
import jmespath


def tag_filter(name, values):
    return {
        "Name": f'tag:{name}',
        "Values": values
    }


class Environment:

    def __init__(self, session: Session, stack_name: str) -> None:
        self.session = session
        self.stack_name = stack_name

    def fetch_instances(self, notebooks: bool = False, database: bool = False, states: list = None):

        filters = []

        filters.append(tag_filter(
            "stack-origin", [self.stack_name]))

        logical_ids = []
        if notebooks:
            logical_ids.append("NBInstance")
        if database:
            logical_ids.append("DBInstance")

        filters.append(tag_filter(
            "aws:cloudformation:logical-id", logical_ids))

        if states:
            filters.append({
                "Name": "instance-state-name",
                "Values": states
            })

        client = self.session.client('ec2')
        response = client.describe_instances(Filters=filters)

        return jmespath.search(
            "Reservations[].Instances[]", response)
