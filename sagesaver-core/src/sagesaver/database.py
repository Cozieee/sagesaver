from abc import ABC, abstractmethod
from datetime import datetime
import logging
import time
import os

import jmespath
import json
from json.decoder import JSONDecodeError

from .environment import environment as env
from .server import Server
from .metadata import metadata_plus as mp
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


def _is_user_collection(s):
    name_arr = s.split('.')

    return (len(name_arr) > 1
            and name_arr[0] not in ['admin', 'local', 'config'])


class Mongo(Database):

    def __init__(self, dump_path, time_limit):
        self.dump_path = dump_path
        super().__init__("mongo", time_limit)


    def get_user_totals(self):
        totals = self.db_client().admin.command('top')['totals']
        user_totals = {k:v for k,v in totals.items() if _is_user_collection(k)}

        return user_totals

    def time_inactive(self, idle_field=None):
        new_totals = self.get_user_totals()

        new_dump = {
            "timestamp": datetime.now().timestamp(),
            "totals": new_totals
        }

        update_dump = True

        try:
            dump_file = open(self.dump_path, "r")

            try:
                old_dump = json.load(dump_file)

                new_activity = json.dumps(
                    old_dump['totals']) != json.dumps(new_totals)

                if not new_activity:
                    update_dump = False

            except JSONDecodeError as e:
                if os.stat(self.dump_path).st_size == 0:
                    idle_field.append(
                        name="No New DB Operations",
                        value=False,
                        details="Empty log file"
                    )

                    return None

                else:
                    raise e

        except FileNotFoundError:
            idle_field.append(
                name="No New DB Operations",
                value=False,
                details="New log file"
            )

            return None
        finally:
            if update_dump:
                with open(self.dump_path, "w") as dump_file:
                    new_dump = {
                        "timestamp": datetime.now().timestamp(),
                        "totals": new_totals
                    }

                    json.dump(new_dump, dump_file)

        if idle_field:
            idle_field.append(
                name="No New DB Operations",
                value=not new_activity
            )

        last_active = datetime.fromtimestamp(old_dump['timestamp'])
        seconds_ago = (datetime.now() - last_active).total_seconds()

        return seconds_ago


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
