import json
from json.decoder import JSONDecodeError
from datetime import datetime, timedelta

from .database import Database
from .utils import seconds_ago
    
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