import subprocess
import sys
import os
import pwd
from typing import Tuple

def subprocess_profile(username):
    pw_record = pwd.getpwnam(username)

    def result():
        os.setgid(pw_record.pw_gid)
        os.setuid(pw_record.pw_uid)

    return {
        "preexec_fn": result,
        "env": {
            "HOME": pw_record.pw_dir,
            "LOGNAME": username,
            "USER": username
        }
    }

class CommandFactory:

    @staticmethod
    def pip_install(packages: list):
        return [sys.executable, "-m", "pip", "install", "--user", "--no-cache-dir"] + packages
    
    @staticmethod
    def python3(script: str):
        return [sys.executable, "-c", f"'{';'.join(script)}'"]


class Process:
    def __init__(self, username=None):
        self.profile = (
            subprocess_profile(username) if username
            else {}
        )

    def execute(self, args, consume=False) -> Tuple[bytes, bytes]:
        p = subprocess.Popen(
            ' '.join(args),
            shell=True,
            stdout=subprocess.PIPE if consume else None,
            **self.profile
        )
        
        return p.communicate()

def install_jupyter(config_file, password):
    process = Process()

    process.execute(
        CommandFactory.pip_install([
            'jupyterlab'
        ])
    )

    out = process.execute(
        CommandFactory.python3([
            'from notebook.auth.security import passwd',
            f'print(passwd("{password}"))'
        ]), consume=True
    )[0]

    password_hash = out.decode().strip()


    


