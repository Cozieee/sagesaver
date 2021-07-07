from datetime import datetime
import logging
import re
import time

from .logging import DateField, IdleField, composeMessage
from .server import Server
from .utils import seconds_ago

logger = logging.getLogger(__name__)
loggerIdle = logging.getLogger(__name__ + ".idle")


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

    def __init__(self, log_path, time_format):
        self.log_path = log_path
        self.time_format = time_format

    def get_last_active_entry(self, truncate_log=False):

        with open(self.log_path, 'r+') as f:
            last_active_entry = None

            for line in f:
                try:
                    entry = JupyterEntry(line, self.time_format)
                    if entry.is_active:
                        last_active_entry = entry
                except AttributeError:
                    continue

            if last_active_entry and truncate_log:
                f.write(last_active_entry)

        return last_active_entry

    def time_inactive(self, truncate_log=True):
        last_entry = self.get_last_active_entry(truncate_log)

        return (seconds_ago(last_entry.time) if last_entry
                else time.clock_gettime(time.CLOCK_BOOTTIME))

    @property
    def idle(self):
        idle_field = IdleField("Server Idle")

        t = int(self.time_inactive(truncate_log=True) / 60)

        idle_field.append(
            name="Over Time Limit",
            value=t > self.time_limit,
            details={
                'Time Inactive': t,
                'Time Limit': self.time_limit
            }
        )

        loggerIdle.debug(
            composeMessage("Check Notebook is Idle",[
                DateField(),
                idle_field
            ])
        )

        return idle_field.idle
