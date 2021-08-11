import json
from datetime import datetime


def is_user_collection(name: str):
    name_arr = name.split('.')

    return (len(name_arr) > 1
            and name_arr[0] not in ['admin', 'local', 'config'])


class Mongo:

    def __init__(self, client, cache):
        self.client = client
        self.cache = cache

    def get_user_totals(self):
        totals = self.client().admin.command('top')['totals']
        user_totals = {k: v for k,
                       v in totals.items() if is_user_collection(k)}

        return user_totals

    def last_active(self):
        new_totals = self.get_user_totals()

        new_dump = {
            "timestamp": datetime.now().timestamp(),
            "totals": new_totals
        }

        new_activity = True

        try:
            old_dump = self.cache.read()

            new_activity = (json.dumps(old_dump['totals']) !=
                            json.dumps(new_totals))
            
        except KeyError:
            return datetime.now()
        finally:
            if new_activity:
                self.cache.write(new_dump)

        return datetime.fromtimestamp(old_dump['timestamp'])
