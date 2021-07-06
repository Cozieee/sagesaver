from abc import ABC, abstractmethod
from datetime import datetime, strftime, timedelta
import os

import jmespath
import json
from json.decoder import JSONDecodeError

from .server import Server
from .metadata import metadata_plus as mp
from .utils import seconds_ago
from .logging import IdleLog


class Database(Server, ABC):

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

    def idle(self):
        time_format = self.conf.autostop.time_format

        idle_log = IdleLog(time_format=time_format)

        t = self.time_inactive(idle_log)

        if idle_log.idle:
            t_limit = int(self.conf['autostop']['time_limit'])

            idle_log.condition(
                t <= t_limit,
                {
                    'Name': 'Over Time Limit',
                    'Details': {
                        'Time Inactive': t,
                        'Time Limit': t_limit
                    }
                }
            )

        if idle_log.idle:
            count_nbs = len(self.find_running_notebooks())

            idle_log.condition(
                count_nbs <= 0,
                {
                    'Name': 'No Running Notebooks',
                    'Details': {
                        'Running Notebooks': count_nbs
                    }
                }
            )
        
        print(idle_log.log)

        return idle_log.idle

class Mongo(Database):

    def time_inactive(self, idle_log = None):
        client = self.db_client()
#         db_log_path = self.conf['autostop']['database_log']

        new_totals = client.admin.command('top')['totals']

        with open("mongo.log", "rw") as dump_file:
            try:
                old_dump = json.load(dump_file)
            except JSONDecodeError as e:
                if idle_log:
                    idle_log.condition(False, {
                        "Name": "No New DB Operations",
                        "Result": "Error",
                        "Details": "file format incorrect"
                    })

                raise e
            finally:
                new_dump = {
                    "timestamp": datetime.now(),
                    "totals": new_totals
                }

                json.dump(new_dump, dump_file)

        new_activity = json.dumps(old_dump['totals']) != json.dumps(new_totals)

        if idle_log:
            idle_log.condition(not new_activity, {
                "Name": "No New DB Operations",
            })

        return seconds_ago(old_dump['timestamp'])

class Mysql(Database):

    def time_inactive(self, log):
        pass
