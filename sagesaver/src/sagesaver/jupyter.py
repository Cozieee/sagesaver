import re
from datetime import datetime

from sagesaver.errors import EntryNotFoundError

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

class JupyterLog():

    def __init__(self, file, time_format):
        self.file = file
        self.time_format = time_format

    @property
    def last_active_entry(self):

        last_active_entry = None

        for line in self.file:
            try:
                entry = JupyterEntry(line, self.time_format)
                if entry.is_active:
                    last_active_entry = entry
            except AttributeError:
                continue
        
        return last_active_entry

class Jupyter():
    def __init__(self, log: JupyterLog):
        self.log = log
    
    def last_active(self):
        try:
            return self.log.last_active_entry.time
        except:
            raise EntryNotFoundError

