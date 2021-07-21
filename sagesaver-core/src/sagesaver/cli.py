from ec2_metadata import ec2_metadata as md
import boto3
import json
import logging
import pkg_resources


def read_conf():
    s = pkg_resources.resource_stream(
        __name__, 'data/default-conf.json').read().decode()
    default_conf = json.loads(s)

    try:
        f = open('/etc/sagesaver-conf.json','r')
    except FileNotFoundError:
        return default_conf

    override_conf = json.load(f)

    return {**default_conf, **override_conf}

server_kw = {}

logger = logging.getLogger('sagesaver.database.idle')
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
logger.addHandler(ch)


def get_interface(conf):

    interface_kw = {}

    interface_type = conf['interface']['type']

    if interface_type == 'user':

        from sagesaver import User
        return User(**interface_kw)

    elif interface_type == 'server':

        interface_kw.update({
            'env_stack': conf['server']['env_stack_name'],
            'session': boto3.Session(region_name=md.region),
            'time_limit': conf['server']['idle_time_limit'] * 60
        })

        server_type = conf['server']['type']

        if server_type == 'database':

            interface_kw.update({
                'stack_origin': conf['database']['st'],
                'database_secret_name': f"{conf['aws']['stack_origin']}-Database-Secret"
            })

            database_type = conf['database']['type']

            if database_type == 'mongo':

                interface_kw.update({
                    'dump_path': conf['mongo']['dump_path']
                })

                from sagesaver import Mongo
                return Mongo(**interface_kw)

            elif database_type == 'mysql':

                from sagesaver import Mysql
                return Mysql(**interface_kw)

            else:
                return ValueError('Database Type is (mongo|mysql)')

        elif server_type == 'notebook':

            interface_kw.update({
                'jupyter_log_path': conf['jupyter']['log_path'],
                'jupyter_time_format': conf['jupyter']['config_time_format']
            })
            
            from sagesaver import Notebook
            return Notebook(**interface_kw)

        else:
            return ValueError('Server Type is (database|notebook)')

    else:
        return ValueError('Interface Type is (server|user)')