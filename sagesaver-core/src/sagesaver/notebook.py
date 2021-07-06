import os
from datetime import datetime, strftime
import re
import time

from .server import Server
from .utils import seconds_ago
from .logging import IdleLog


class JupyterEntry():
    def __init__(self, line, time_format):
        self._line = line
        self._time_format = time_format

    @property
    def time(self):
        m = re.match(r'\[[A-Z] (.*)\.\d* [a-zA-Z]*\]', self._line)
        return datetime.strptime(m.group(1), self._time_format)

    @property
    def is_active(self):
        m = re.match(r'\[([A-Z]).*](.*)', self._line)

        log_level = m.group(1)
        description = m.group(2)

        return (
            log_level != 'D' or
            description.startswith("activity on")
        )

    def __repr__(self):
        return self._line


class Notebook(Server):

    def get_last_active_entry(self, truncate_log = False):
        time_format = self.conf.jupyter.time_format

        with open(self.path, 'rw') as f:
            last_active_entry = None

            for line in f:
                try:
                    entry = JupyterEntry(line, time_format)
                    if entry.is_active:
                        last_active_entry = entry
                except AttributeError:
                    continue
            
            if last_active_entry and truncate_log:
                f.write(last_active_entry)

        return last_active_entry

    def time_inactive(self, *args):
        last_entry = self.get_last_active_entry(*args)

        return (seconds_ago(last_entry.time) if last_entry
                else time.clock_gettime(time.CLOCK_BOOTTIME))

    @property
    def idle(self):
        time_format = self.conf.jupyter.time_format
        idle_log = IdleLog(time_format)

        t = self.time_inactive(truncate_log=True)
        t_limit = self.conf.autostop.time_limit

        idle_log.condition(t <= t_limit, {
            'Name': 'Under Time Limit',
            'Details': {
                'Time Inactive': t,
                'Time Limit': t_limit
            }
        })

        print(idle_log.log)

        return idle_log.idle

