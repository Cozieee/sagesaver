import os
import argparse
from datetime import datetime
import json
from json.decoder import JSONDecodeError
from bson import json_util
import jmespath
import boto3
from pymongo import MongoClient
from config import config

REGION = config["aws"]["region"]
VPC_ID = config["aws"]["vpc-id"]
STACK_NAME = config["aws"]["stack"]
DB_CONNECTION_STRING = config["aws"]["conn-str"]

TIME_LIMIT = config["autostop"]["time_limit"]
DB_LOG_PATH = config["autostop"]["db_log"]["path"]
OUTPUT_TIME_FORMAT = config["autostop"]["output"]["time_format"]

def exclude_admin_collections(top_dict):
    
    def is_user_coll(str):
        return str.split('.')[0] not in ['admin', 'config', 'local']
    
    filter_dict = {}
    for k, v in top_dict.items():
        if is_user_coll(k):
            filter_dict[k] = v
    
    return filter_dict

def new_operations(old, new):
    if old.keys() != new.keys():
        return None
    
    n = 0
    
    for k in old.keys():
        old_n = old[k]['total']['count']
        new_n = new[k]['total']['count']
        
        n += new_n - old_n
    
    return n

def notebooks_running(zone, stack):
    """Count Number of notebook servers currently
    running in a stack
    
    Args:
        region: Availability zone the stack's vpc is in
        vpc: Id of the VPC the stack is hosted
        stack: Name of the stack
        
    Returns:
        Number of stack notebook servers that are running
    """
    ec2 = boto3.client('ec2', zone)
    
    filters = [
        {
            "Name": "tag:sagesaver:stack-origin",
            "Values": [stack]
        },
        {
            "Name": "tag:sagesaver:server-type",
            "Values": ["Notebook"]
        },
        {
            "Name": "instance-state-name",
            "Values": ["running", "pending"]
        }
    ]
    
    response = ec2.describe_instances(Filters = filters)
    notebook_instances = jmespath.search("Reservations[].Instances[].InstanceId", response)

    return notebook_instances

def seconds_ago(time):
    return (datetime.now() - time).total_seconds()

def main():
    client = MongoClient(DB_CONNECTION_STRING)
    
    old_user_log = {}
    
    # Time of last update
    old_timestamp = datetime.now() # defaults to now
    
    # Attempt to load existing log
    try:
        with open(DB_LOG_PATH) as infile:
            old_user_log = json.load(infile, object_hook = json_util.object_hook)
            
            # Use given last-update timestamp from existing log
            old_timestamp = datetime.fromtimestamp(old_user_log["timestamp"])
            
            # Must remove timestamp field for new operation comparison
            del old_user_log["timestamp"]
    except (FileNotFoundError, JSONDecodeError):
        # First log fetch fakes new operation with auxillary field
        old_user_log["aux"] = None
    
    # Create new log from totals
    new_user_log = client.admin.command('top')['totals']
    
    # Filter log fields for user-generated collections only
    new_user_log = exclude_admin_collections(new_user_log)
    del new_user_log["note"]
    
    print(f'[{datetime.now().strftime(OUTPUT_TIME_FORMAT)}]', end=' ')
    
    # Count number of new operations
    ops = new_operations(old_user_log, new_user_log)
    pred = ops != 0
    print(f"OPS: {'YES' if pred else 'NO'}", end = ' ' if pred else ' | ')
    
    # If new operations, dump new log
    if pred:
        print(f"({'meta' if ops == None else ops})", end = " => ")
        with open(DB_LOG_PATH, 'w') as outfile:
            # Include current timestamp into new log
            new_user_log["timestamp"] = datetime.now().timestamp()
            json.dump(new_user_log, outfile, default = json_util.default)
            
        return print('New log saved')
    
    secs_idle = seconds_ago(old_timestamp)
    
    pred = secs_idle < TIME_LIMIT
    print(f"TIME: {'OK' if pred else 'EXCEEDED'} ({secs_idle:.0f}s)", end = ' ' if pred else ' | ')
    
    # Don't shutdown if idle time has not exceeded limit
    if pred:
        return print('Shutdown not met')
    
    # Count Notebooks running
    count_nbs = len(notebooks_running(REGION, STACK_NAME))
    pred = count_nbs > 0
    print(f"NBS: {count_nbs}", end = ' ' if pred else ' | ')
    
    # Don't shutdown if there are notebook servers are running
    if pred: 
        return print('Shutdown not met')
        
    print('Shutting down...')
    os.system('sudo shutdown now -h')
    
main()
