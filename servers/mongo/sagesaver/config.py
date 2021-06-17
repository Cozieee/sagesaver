import json
import os

SAGESAVER_CONFIG_PATH = os.environ['SAGESAVER_CONFIG_PATH'] or "/etc/sagesaver/config.json"

with open(SAGESAVER_CONFIG_PATH, 'r') as infile:
    config = json.load(infile)
