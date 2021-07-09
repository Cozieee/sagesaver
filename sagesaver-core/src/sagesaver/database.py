from abc import ABC, abstractmethod
from datetime import datetime
import logging
import time

import jmespath
import json
from json.decoder import JSONDecodeError

from .environment import environment as env
from .server import Server
from .metadata import metadata_plus as mp
from .utils import seconds_ago
from .logging import DateField, IdleField, composeMessage

logger = logging.getLogger(__name__)
loggerIdle = logging.getLogger(__name__ + ".idle")


class Database(Server, ABC):

    def __init__(self, type, time_limit):
        self.type = type
        self.time_limit = time_limit
        super().__init__()

    @abstractmethod
    def time_inactive(self):
        pass

    def find_running_notebooks(self):
        """List notebook servers currently running in a stack

        Returns:
            list(ec2 id): Stack notebook servers that are running
        """

        filters = [
            {
                "Name": "tag:stack-origin",
                "Values": [mp.tags['stack-origin']]
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

        t = self.time_inactive(idle_field)
        if idle_field.idle:
            t_limit = self.time_limit

            idle_field.append(
                name="Over Time Limit",
                value=t > t_limit,
                details={
                    "Time Inactive": t,
                    "Time Limit": t_limit
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
            composeMessage(f"Check {self.type.capitalize()} DB Idle", [
                DateField(),
                idle_field
            ])
        )

        return idle_field.idle


class Mongo(Database):

    def __init__(self, dump_path, time_limit):
        self.dump_path = dump_path
        super().__init__("mongo", time_limit)

    def time_inactive(self, idle_field=None):
        client = self.db_client()

        new_totals = client.admin.command('top')['totals']

        with open(self.dump_path, "r+") as dump_file:
            try:
                old_dump = json.load(dump_file)
            except JSONDecodeError as e:
                if idle_field:
                    idle_field.condition(
                        name="No New DB Operations",
                        value=False,
                        details="New file"
                    )
                raise e
            finally:
                new_dump = {
                    "timestamp": datetime.now(),
                    "totals": new_totals
                }

                json.dump(new_dump, dump_file)

        new_activity = json.dumps(old_dump['totals']) != json.dumps(new_totals)

        if idle_field:
            idle_field.append(
                name="No New DB Operations",
                value=not new_activity
            )

        return seconds_ago(old_dump['timestamp'])


class Mysql(Database):

    def __init__(self, log_path, time_limit):
        self.log_path = log_path
        super().__init__("mysql", time_limit)

    def get_last_active_entry(self):
        with open(self.log_path, 'r') as log_file:
            last_entry = None

            for line in log_file.readlines():
                try:
                    date_str = line.split()[0]
                    datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S.%fZ')
                except (IndexError, ValueError):
                    continue
                else:
                    last_entry = line

            return last_entry

    def time_inactive(self, idle_field=None, truncate_log=True):
        last_entry = self.get_last_active_entry()

        if last_entry:
            if truncate_log:
                with open(self.log_path, 'w') as log_file:
                    log_file.write(last_entry)

            entry_date = datetime.strptime(
                last_entry.split()[0], '%Y-%m-%dT%H:%M:%S.%fZ')
            return seconds_ago(entry_date)
        else:
            logger.warning(
                f"{__name__} > Found no log entries in mysql.log")
            return time.clock_gettime(time.CLOCK_BOOTTIME)
