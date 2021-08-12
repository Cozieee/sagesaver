from . import execute
import shutil
from pathlib import Path
from jinja2 import Template
from pymysql import Connection

from . import PACKAGE_PATH


class TemplateWriter():

    def __init__(self, username=None):
        self.username = username

    def write(self, in_path, out_path, renderer=None, **kwargs):

        with open(in_path) as config_in, open(out_path) as config_out:
            template = Template(config_in.read())
            rendered = (renderer(template, **kwargs) if renderer
                        else template.render(**kwargs))

            config_out.write(rendered)

            if self.username:
                shutil.chown(out_path, user=self.username, group=self.username)

def single_line(out: bytes, *_):
    return out.decode().strip()

def home_path(user=None):
    return Path(execute.bash(
        ['echo', '$HOME'],
        username=user, consumer=single_line))


def get_hash(password, user=None):
    return execute.python3([
        'from notebook.auth.security import passwd',
        f'print(passwd("{password}"))'
    ], username=user, consumer=single_line)

def install_community(user=None):
    execute.bash([
        'rpm -Uvh https://dev.mysql.com/get/mysql57-community-release-el7-11.noarch.rpm;',
        'yum install -y mysql-community-server;',
        'systemctl enable mysqld;',
        'systemctl start mysqld'
    ], username=user)


def jupyter(password, host_user='ec2-user', port=8888):
    templater = TemplateWriter(host_user)

    execute.pip_install([
        'jupyterlab'
    ], username=host_user)

    in_path = home_path(host_user) / '.jupyter'
    out_path = PACKAGE_PATH / 'jupyter_lab_config.py'

    templater.write(in_path, out_path,
                    password_hash=get_hash(host_user),
                    port=port)

def mysql_temporary_password(log_file):
    line = ""
    while "A temporary password is generated" not in line:
        line = log_file.readline()

    return line.split()[-1]
    
def mysql(username, password, log_path, host_user='ec2-user'):
    install_community(host_user)

    with open('/var/log/mysqld.log') as log_file:
        temporary_password = mysql_temporary_password(log_file)

    execute.bash([
        'mysqladmin',
        '--user=root', 
        f"--password='{temporary_password}'", 
        'password', 
        password
    ])




    


    
    

    

