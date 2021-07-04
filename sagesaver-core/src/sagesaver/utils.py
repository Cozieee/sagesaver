from datetime import datetime

def seconds_ago(time):
    return (datetime.now() - time).total_seconds()