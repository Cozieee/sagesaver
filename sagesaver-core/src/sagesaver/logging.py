from datetime import datetime, strftime


class Log(object):

    def __init__(self, time_format="%Y-%m-%d %H:%M:%S"):
        self.time_format = time_format

    def log(self, details = {}):
        return {
            'Date': strftime(datetime.now(), self.time_format),
            **details
        }


class IdleLog(Log):

    _idle = False
    _log = {
        'Conditions': [],
        'Idle': False
    }

    def condition(self, result, log=None):
        if log:
            if 'Result' not in log:
                log['Result'] = result

            self.log['Conditions'].append(log)

            self._idle &= result

    @property
    def log(self):
        return super.log(self._log)

    @property
    def idle(self):
        return self._idle
