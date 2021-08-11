from boto3.session import Session
import click
from sagesaver.environment import Environment
from sagesaver.shutdown import check_no_active_notebooks

@click.group()
def entrypoint():
    pass

entrypoint.add_command()