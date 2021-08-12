import subprocess
import sys
import os
from pathlib import Path
import pwd

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

def single_line(out: bytes, *_):
    return out.decode().strip()

class Execution:

    def __init__(self, username=None):
        self._username = username
    
    def switch(self, username):
        self._username = username

    def bash(self, command, consumer = None):
        profile = (
            subprocess_profile(self._username) if self._username
            else {}
        )

        p = subprocess.Popen(
            ' '.join(command),
            shell=True,
            stdout=subprocess.PIPE if consumer else None,
            **profile
        )

        result = p.communicate()
        return consumer(result) if consumer else None

    def pip_install(self, packages: list):
        return self.bash([sys.executable, "-m", "pip", "install", "--user", "--no-cache-dir"] + packages)

    def python3(self, script: list):
        return self.bash([sys.executable, "-c", f"'{';'.join(script)}'"])

    def home_path(self):
        return Path(self.bash(
            ['echo', '$HOME'], consumer=single_line))