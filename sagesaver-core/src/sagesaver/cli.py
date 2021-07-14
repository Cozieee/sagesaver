from ec2_metadata import ec2_metadata as md
import boto3
import json
import logging

server_kw = {}

logger = logging.getLogger('sagesaver.database.idle')
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
logger.addHandler(ch)

with open('/etc/sagesaver.conf') as conf_file:
    conf = json.load(conf_file)

    server_type = conf['aws']['server_type']

    server_kw.update({
        'session': boto3.Session(region_name=md.region),
        'time_limit': conf['autostop']['time_limit'] * 60
    })

    if server_type == 'database':
        
        database_type = conf['aws']['database_type']

        server_kw.update({
            'stack_origin': conf['aws']['stack_origin'],
            'database_secret_name': f"{conf['aws']['stack_origin']}-Database-Secret"
        })

        if database_type == 'mongo':
            server_kw.update({
                'dump_path': conf['mongo']['dump_path']
            })

            from sagesaver import Mongo
            server = Mongo(**server_kw)


        elif database_type == 'mysql':
            from sagesaver import Mysql
            server = Mysql(**server_kw)

    elif server_type == 'notebook':
        pass