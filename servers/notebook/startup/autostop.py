import os
import re
from datetime import datetime
import jmespath

from config import config
autostop = config['autostop']

def get_log_time(line):
    m = re.match(r'\[[A-Z] (.*)\.\d* [a-zA-Z]*\]', last_line)
    return datetime.strptime(m.group(1), "%Y-%m-%d %H:%M:%S")

def is_active_line(line):
    m = re.match(r'\[([A-Z]).*](.*)', line)
    
    log_level = m.group(1)
    description = m.group(2)

    return (
        log_level != 'D' or 
        description.startswith(" activity on")
    )

def get_last_active(path):
    with open(path, 'r') as f:
        last_active_line = None
        
        for line in f:
            try:
                if is_active_line(line):
                    last_active_line = line
            except AttributeError:
                pass
                
    return last_active_line

def seconds_ago(time):
    return (datetime.now() - time).total_seconds()

last_line = get_last_active(autostop["log_path"])
seconds_idle = seconds_ago(get_log_time(last_line))

print(f'[{datetime.now().strftime(autostop["log_time_format"])}] Last active {seconds_idle:.0f}s ago')

with open(autostop["log_path"], 'w') as f:
    f.write(last_line)

if seconds_idle > autostop["time_limit"]:
    print(f'Idle Limit ({autostop["time_limit"]}s) exceeded. Shutting down...')
    os.system('sudo shutdown now -h')