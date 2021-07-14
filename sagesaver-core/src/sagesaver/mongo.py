from datetime import datetime
import json
from json.decoder import JSONDecodeError
import logging
import os

from pymongo import MongoClient

from .database import Database, SupportedDBMS

logger = logging.getLogger(__name__)


def _is_user_collection(s):
    name_arr = s.split('.')

    return (len(name_arr) > 1
            and name_arr[0] not in ['admin', 'local', 'config'])

class Mongo(Database):

    def __init__(
        self,
        dump_path,
        **kwargs
    ):
        self.dump_path = dump_path
        super().__init__(dbms_type = SupportedDBMS.MONGO, **kwargs)

    def client(self, **kwargs):
        secret = self.get_secret(self.database_secret_name)

        return MongoClient(
            username=secret['username'],
            password=secret['password'],
            port=secret['port'],
            host=secret['host'],
            **kwargs
        )

    def get_user_totals(self):
        totals = self.client().admin.command('top')['totals']
        user_totals = {k: v for k,
                       v in totals.items() if _is_user_collection(k)}

        return user_totals
    
    def last_active(self, idle_field=None):
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

        return last_active
