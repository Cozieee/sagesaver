from collections import ChainMap
from datetime import datetime


def composeMessage(topic=None, fields=[], stringify=True, details={}):
    message_fields = []

    if topic:
        message_fields.append(("Topic", topic))

    message_fields.extend(
        list(map(lambda f: f(), fields))
    )

    message_dict = dict(message_fields)
    message_dict.update(details)

    return str(message_dict) if stringify else message_dict


class Field():

    def __init__(self, key=None):
        if key:
            self.key = key

    @property
    def value(self):
        return None

    def __call__(self):
        return self.key, self.value


class HistoryMixin():

    _history = []

    def reduce(self):
        pass

    def append(self, name, value, details=None):
        entry = {
            'Name': name,
            'Value': value,
        }

        if details:
            entry['Details'] = details
        
        self._history.append(entry)
        self.reduce(value)


class DateField(Field):

    key = "Date"

    def __init__(self, time_format="%Y-%m-%d %H:%M:%S"):
        self.time_format = time_format

    @property
    def value(self):
        return datetime.now().strftime(self.time_format)


class IdleField(Field, HistoryMixin):

    key = "Idle"
    _idle = True

    def reduce(self, condition):
        self._idle &= condition

    @property
    def idle(self):
        return self._idle

    @property
    def value(self):
        passed_conditions = list(filter(lambda d: d['Value'], self._history))
        failed_conditions = list(
            filter(lambda d: not d['Value'], self._history))

        return {
            "Verdict": self._idle,
            "Passed": passed_conditions,
            "Failed": failed_conditions
        }
