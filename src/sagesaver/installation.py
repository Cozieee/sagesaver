from pathlib import Path
import shutil
from jinja2 import Environment, PackageLoader, StrictUndefined
import pymongo
from pymongo.mongo_client import MongoClient
import pymysql
from .execute import Execution, single_line
from . import PACKAGE_NAMESPACE

root = Execution()
template_env = Environment(
    loader=PackageLoader(PACKAGE_NAMESPACE, "templates"), 
    undefined=StrictUndefined
)

class JupyterInstallation:

    def __init__(self, default_user: Execution):
        self.default_user = default_user

    def install_dependencies(self):
        return self.default_user.pip_install([
            'jupyterlab'
        ])

    def get_hash(self, password):
        return self.default_user.python3([
            'from notebook.auth.security import passwd',
            f'print(passwd("{password}"))'
        ], single_line)

    def __call__(self, password, port=8888):
        out_path = self.default_user.home_path() / '.jupyter' / 'jupyter_lab_config.py'

        template_env.get_template(
            "jupyter_lab_config.py.jinja"
        ).stream(
            password_hash=self.get_hash(password),
            port=port
        ).dump(out_path)

        shutil.chown(out_path, user=self.default_user.username,
                     group=self.default_user.username)


def link_log(conn, log_path: Path):
    log_path.touch(exist_ok=True)
    shutil.chown(log_path, user='mysql', group='mysql')

    with conn.cursor() as cursor:
        cursor.execute("SET GLOBAL log_output = %s", ('FILE'))
        cursor.execute("SET GLOBAL general_log_file = %s", (log_path))
        cursor.execute("SET GLOBAL general_log = %s", ('ON'))


def create_mysql_user(conn, username, password, host):
    with conn.cursor() as cursor:
        cursor.execute("CREATE USER %s@%s IDENTIFIED BY %s",
                       (username, host, password))
        cursor.execute('FLUSH PRIVILEGES')


def mysql_super_user(conn, username, host):
    with conn.cursor() as cursor:
        cursor.execute('GRANT ALL ON *.* TO %s@%s', (username, host))


class MysqlInstallation:

    def __init__(self, log_path):
        self.log_path = log_path

    def initialize_mariadb(self, password):
        root.bash([
            'rpm -Uvh https://dev.mysql.com/get/mysql57-community-release-el7-11.noarch.rpm;',
            'yum install -y mysql-community-server;',
            'systemctl enable mysqld;',
            'systemctl start mysqld'
        ], username=self._username)

        root.bash([
            'mysqladmin',
            '--user=root',
            'password',
            password
        ])

    def __call__(self, username, password):
        self.initialize_mariadb(password)

        with pymysql.connect(password=password) as connection:

            allowed_host = "%"
            create_mysql_user(connection, username, password, allowed_host)
            mysql_super_user(connection, username, allowed_host)

            link_log(connection, self.log_path)

            connection.commit()

class XFSVolume:
    def __init__(self, partition_id):
        self.partition_path = Path('/dev') / partition_id

    def mount(self, dir: Path, label=None):
        dir.mkdir()

        cmd = ['mkfs.xfs']
        if label:
            cmd.extend(['-L', label])
        cmd.append(dir)
        root.bash(cmd)

        root.bash(
            ['mount', '-t', 'xfs', self.partition_path, dir])

        with open('/etc/fstab', 'a') as f:
            f.write(' '.join[self.partition_path, dir,
                             'xfs defaults,auto,noatime,noexec 0 0'])

def create_admin_user(admin, username, password):
    admin.add_user(username, password, roles=["root"])

def newlines(l):
    return list(map(lambda s: '\n' + s, l))

class MongoInstallation:

    service = 'mongod'

    def __init__(
        self,
        data_dest: Path = Path('/var/lib/mongo'),
        log_dest: Path = Path('/var/log/mongodb/mongod.log'),
        port = 27017
    ):
        self.data_dest = data_dest
        self.log_dest = log_dest
        self.port = port

    def initialize_mongo(self):

        template_env.get_template(
            "mongodb-org-4.4.repo.jinja"
        ).stream().dump("/etc/yum.repos.d/mongodb-org-4.4.repo")
        root.bash(['yum', '-y', 'install', 'mongodb-org'])

    def mount_volumes(self, volumes):
        service_dests = []

        volumes['data'].mount(self.data_dest)
        service_dests.append(self.data_dest)

        if 'journal' in volumes:
            journal_dest = self.data_dest / 'journal'
            volumes['journal'].mount(journal_dest)
            service_dests.append(journal_dest)

        if 'log' in volumes:
            volumes['log'].mount(self.log_dest)
            service_dests.append(self.log_dest)

        for dest in service_dests:
            shutil.chown(dest, self.service, self.service)

    def optimize_conf(self):
        with open('/etc/security/limits.conf', 'a') as f:
            f.writelines(newlines([
                "* soft nofile 64000",
                "* hard nofile 64000",
                "* soft nproc 32000",
                "* hard nproc 32000",
            ]))

        with open('/etc/security/limits.d/90-nproc.conf', 'a') as f:
            f.writelines(newlines([
                "* soft nproc 32000",
                "* hard nproc 32000",
            ]))

        template_env.get_template(
            'disable-transparent-hugepages.jinja'
        ).stream().dump('/etc/init.d/disable-transparent-hugepages')

        template_env.get_template(
            'logrotate.d-mongodb.jinja'
        ).stream().dump('/etc/logrotate.d/mongodb')

    def override_mongo_conf(self):
        template_env.get_template(
            "mongod.conf.jinja"
        ).stream(
            log_path = self.log_dest,
            data_path = self.data_dest,
            port = self.port
        ).dump("/etc/mongod.conf")

    def __call__(self, username, password, volumes=None):
        if volumes:
            self.mount_volumes(volumes)

        self.initialize_mongo()

        service_str = f'{self.service}.service'
        root.bash([
            f'systemctl enable {service_str};',
            f'systemctl start {service_str}'
        ])

        create_admin_user(pymongo.MongoClient().admin, username, password)

        self.optimize_conf()
        self.override_mongo_conf()

        root.bash(['sytemctl', 'restart', {service_str}])