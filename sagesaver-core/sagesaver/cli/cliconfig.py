import json

from sagesaver import PACKAGEDIR

entity_conf_path = f'{PACKAGEDIR}/data/entity-conf.json'

def load_config():
    with open(entity_conf_path, 'r') as f:
        base_conf = json.load(f)

    custom_conf_path = base_conf['custom_conf']

    if custom_conf_path is not None:
        with open(custom_conf_path, 'r') as f:
            custom_conf = json.load(f)

        base_conf = {**base_conf, **custom_conf}

    return base_conf

def save_config(config):
    with open(entity_conf_path, 'w') as f:
        json.dump(config, f, indent=4)

class ConfigManager():
    def __init__(self):
        self.config = load_config()

    def update(self, scope, fields):
        if scope not in self.config:
            raise KeyError
        
        self.config[scope].update(fields)
        save_config(self.config)

