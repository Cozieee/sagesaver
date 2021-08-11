import time
from datetime import datetime

from .environment import Environment

def seconds_ago(t):
    return (datetime.now() - t).total_seconds()

class ServerIdleCheck():

    def __init__(self, server, idle_limit: int):
        self.server = server
        self.idle_limit = idle_limit

    @staticmethod
    def boot_time():
        time.clock_gettime(time.CLOCK_BOOTTIME)

    def run(self):
        seconds_inactive = seconds_ago(self.server.last_active())
        time_inactive = seconds_inactive and self.boot_time()

        return time_inactive < self.idle_limit


class NoActiveNotebooksCheck():

    def __init__(self, environment: Environment):
        self.environment = environment

    def run(self):
        active_notebooks = self.environment.fetch_instances(
            notebooks=True, states=["running", "pending"])

        return len(active_notebooks) == 0

class IdleDelayExpiredCheck():

    def __init__(self, cache):
        self.cache = cache
    
    def seconds_delayed(self):
        try:
            expiration_time = datetime.fromtimestamp(self.cache.read())
        except KeyError:
            return None
        
        return seconds_ago(expiration_time)

    def run(self):
        return self.seconds_delayed and self.seconds_delayed > 0