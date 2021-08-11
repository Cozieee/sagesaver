from datetime import datetime

from sagesaver.errors import EntryNotFoundError


class MysqlEntry():

    def __init__(self, line):
        self.line = line

        line_arr = line.split()
        self.time = datetime.strptime(line_arr[0], '%Y-%m-%dT%H:%M:%S.%fZ')


class MysqlLog():
    def __init__(self, file):
        self.file = file

    @property
    def last_active_entry(self):
        last_entry = None

        for line in self.file.readlines():
            try:
                entry = MysqlEntry(line)
            except (IndexError, ValueError):
                continue
            else:
                last_entry = entry

        return last_entry

class Mysql:
    def __init__(self, log):
        self.log = log
    
    def last_inactive(self):
        try:
            return self.log.last_active_entry.time
        except:
            raise EntryNotFoundError
