from datetime import datetime
from sagesaver.server import Server
from sagesaver.logging import *

# def get_log_time(line):
#     m = re.match(r'\[[A-Z] (.*)\.\d* [a-zA-Z]*\]', last_line)
#     return datetime.strptime(m.group(1), JUPYTER_LOG_TIME_FORMAT)

# def is_active_line(line):
#     m = re.match(r'\[([A-Z]).*](.*)', line)

#     log_level = m.group(1)
#     description = m.group(2)

#     return (
#         log_level != 'D' or 
#         description.startswith(" activity on")
#     )
    
class Notebook(Server):

    def get_last_active(self):

        with open(path, 'r') as f:
            last_active_line = None

            for line in f:
                try:
                    if is_active_line(line):
                        last_active_line = line
                except AttributeError:
                    pass

        return last_active_line

#     def autostop(self):
#         log = ConditionsLog(" | ")
        
#         last_line = get_last_active(self.conf['jupyter']['log'])
#         seconds_idle = seconds_ago(get_log_time(last_line))

#     print(f'[{datetime.now().strftime(OUTPUT_TIME_FORMAT)}] Last active {seconds_idle:.0f}s ago')

#     with open(JUPYTER_LOG_PATH, 'w') as f:
#         f.write(last_line)

#     if seconds_idle > INACTIVE_TIME_LIMIT:
#         print(f'Idle Limit ({INACTIVE_TIME_LIMIT}s) exceeded. Shutting down...')
#         os.system('sudo shutdown now -h')