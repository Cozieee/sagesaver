from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
import logging
import time

import jmespath

from .server import Server
from ..logging.fields import DateField, IdleField, composeMessage

logger = logging.getLogger(__name__)
loggerIdle = logging.getLogger(__name__ + ".idle")


class SupportedDatabases(Enum):
    MONGO = ('MongoDB')
    MYSQL = ('MySQL')

    def __init__(self, proper_name):
        self.proper_name = proper_name

    def __repr__(self):
        return self.proper_name
    
    def __str__(self):
        return self.proper_name


class Database(Server, ABC):

    def __init__(
        self,
        secret_name,
        database_type,
        **kwargs
    ):
        if not isinstance(database_type, SupportedDatabases):
            raise TypeError(f'Provided dbms type is not supported')

        self.secret_name = secret_name
        self.database_type = database_type

        super().__init__(**kwargs)

    @abstractmethod
    def last_active(self):
        pass

    def find_running_notebooks(self):
        """List notebook servers currently running in a stack

        Returns:
            list(ec2 id): Stack notebook servers that are running
        """

        filters = [
            {
                "Name": "tag:stack-origin",
                "Values": [self.env_stack]
            },
            {
                "Name": "tag:server-type",
                "Values": ["notebook"]
            },
            {
                "Name": "instance-state-name",
                "Values": ["running", "pending"]
            }
        ]

        client = self.session.client('ec2')
        response = client.describe_instances(Filters=filters)
        notebook_instances = jmespath.search(
            "Reservations[].Instances[].InstanceId", response)

        return notebook_instances

    @property
    def idle(self):
        idle_field = IdleField("Server Idle")

        last_active = self.last_active(idle_field)

        if idle_field.idle:
            time_inactive = time.clock_gettime(time.CLOCK_BOOTTIME)

            if last_active:
                time_inactive = (datetime.now() - last_active).total_seconds()

            idle_field.append(
                name="Over Time Limit",
                value=time_inactive > self.time_limit,
                details={
                    "Time Inactive": time_inactive,
                    "Time Limit": self.time_limit
                }
            )

        if idle_field.idle:
            count_nbs = len(self.find_running_notebooks())

            idle_field.append(
                name="No Running Notebooks",
                value=count_nbs == 0,
                details={
                    'Running Notebooks': count_nbs
                }
            )

        loggerIdle.debug(
            composeMessage(f"Checking {self.database_type} Server idle", [
                DateField(),
                idle_field
            ])
        )

        return idle_field.idle
