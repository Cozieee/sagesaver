import boto3

from .. import mysql, mongo, notebook, user

class EnvironmentFactory():

    generator: callable = None

    def __init__(self, config):
        self.config = config

    def load_params(self):
        super.load_params()

        d = self.config['environmental']
        
        self.params.update({
            'stack_name': d['stack_name'],
            'session': boto3.session.Session(region_name=d['region'])
        })

    def generate_entity(self):
        if self.generator is None:
            raise Exception('Generator not defined for intermediate factories')
        
        self.load_params()
        return self.generator(self.params)

class ServerFactory(EnvironmentFactory):

    def load_params(self):
        super.load_params()

        d = self.config['server']

        self.params.update({
            'time_limit': d['time_limit'] * 60
        })

class UserFactory(EnvironmentFactory):
    
    generator = user.User

class NotebookFactory(ServerFactory):

    generator = notebook.Notebook

    def load_params(self):
        super.load_params()

        d = self.config['notebook']
        
        self.params.update({
            'jupyter_log_path': d['log_path'],
            'jupyter_time_format': d['config_time_format']
        })
    
class DatabaseFactory(ServerFactory):

    def load_params(self):
        super.load_params()

        d = self.config['database']
        
        self.params.update({
            'secret_name': d['secret_name']
        })
        
class MongoFactory(DatabaseFactory):

    generator = mongo.Mongo

    def load_params(self):
        super.load_params()

        d = self.config['database']
        
        self.params.update({
            'secret_name': d['secret_name']
        })

class MysqlFactory(DatabaseFactory):

    generator = mysql.Mysql

    def load_params(self):
        super.load_params()

        d = self.config['database']
        
        self.params.update({
            'secret_name': d['secret_name']
        })


