import os
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
import json
from json.decoder import JSONDecodeError

from .server import Server
from .metadata import metadata_plus as mp
from .utils import seconds_ago
    
class Database(Server, ABC):
    
    @abstractmethod
    def time_inactive(self, log):
        pass
    
    def find_running_notebooks(self):
        """List notebook servers currently running in a stack

        Returns:
            list(ec2 id): Stack notebook servers that are running
        """

        filters = [
            {
                "Name": "tag:stack-origin",
                "Values": [mp.tags['stack-origin']]
            },
            {
                "Name": "tag:server-type",
                "Values": ["notebook"]
            },
            {
                "Name": "instance-state-name",
                "Values": ["running", "pending"]
            }
        ]

        client = self.session.client('ec2')
        response = client.describe_instances(Filters = filters)
        notebook_instances = jmespath.search("Reservations[].Instances[].InstanceId", response)

        return notebook_instances
    
    def autostop(self):
        log = ConditionsLog(entry_delim=' | ')
        shutdown = True
        
        if shutdown:
            t = self.time_inactive(log)
            t_limit = int(self.conf['autostop']['time_limit'])

            time_cond = UnderTimeLimit(t, t_limit)
            log.add_entry(time_cond)

            shutdown &= not bool(time_cond)
        
        if shutdown:
            count_nbs = len(self.find_running_notebooks())
            
            nbs_cond = HasRunningNotebooks(count_nbs)
            log.add_entry(nbs_cond)
            
            shutdown &= not bool(nbs_cond)
        
        action = "Shutting down" if shutdown else "Shutdown not met"
        print(f"[{datetime.now()}]", log, "=>", action)
            
        if shutdown:
#             os.system('sudo shutdown now -h')
            pass

class Mongo(Database):
    
    def time_inactive(self, log):
        client = self.db_client()
#         db_log_path = self.conf['autostop']['database_log']
        db_log_path = "db.log"
        
        new_totals = client.admin.command('top')['totals']
        
        # Update last active with database log
        try:
            with open(db_log_path) as infile:
                old_db_log = json.load(infile)
                old_totals = old_db_log['totals']
                
                new_activity = json.dumps(old_totals) != json.dumps(new_totals)
                last_active = (datetime.now() if new_activity else 
                               datetime.fromtimestamp(old_db_log["timestamp"]))
                existing_log = True
        
        # First log
        except (FileNotFoundError, JSONDecodeError):
            
            db_uptime = client.admin.command("serverStatus")["uptime"]
            
            new_activity = True
            last_active = datetime.now() - timedelta(seconds=db_uptime)
            existing_log = False
        
        log.append({
            "Name": "New DB operations",
            "Value": new_activity,
            "Details": {
                "Existing Log": existing_log
            }
        })

        # Dump new database log
        
        if new_activity:
            with open(db_log_path, 'w') as outfile:
                new_user_log = {
                    "timestamp": last_active.timestamp(),
                    "totals": new_totals
                }

                json.dump(new_user_log, outfile)
            
            return -1

        return seconds_ago(last_active)

class Mysql(Database):
    
    def time_inactive(self, log):