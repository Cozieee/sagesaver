from datetime import datetime
import time
import logging

from pymysql import Connection

from .database import Database, SupportedDatabases

logger = logging.getLogger(__name__)


class Mysql(Database):

    def __init__(self, log_path, *args, **kwargs):
        self.log_path = log_path
        super().__init__(*args, **kwargs, dbms_type=SupportedDatabases.MYSQL)

    def connection(self, **kwargs):
        secret = self.get_secret(self.database_secret_name)

        return Connection(
            user=secret['username'],
            password=secret['password'],
            port=secret['port'],
            host=secret['host'],
            **kwargs
        )

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

    def last_active(self, idle_field=None, truncate_log=True):
        last_entry = self.get_last_active_entry()

        if last_entry:
            if truncate_log:
                with open(self.log_path, 'w') as log_file:
                    log_file.write(last_entry)

            last_active = datetime.strptime(
                last_entry.split()[0], '%Y-%m-%dT%H:%M:%S.%fZ')

            return last_active
        else:
            logger.warning(
                f"{__name__} > Found no log entries in mysql.log")
            return None
