from functools import wraps
import subprocess
import sys
import os
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


def command(user = None):
    def wrapper_factory(command_factory):
        @wraps(command_factory)
        def wrapper(*args, username: str = user, consumer = None, **kwargs):
            command_arr = command_factory(*args, **kwargs)

            profile = (
                subprocess_profile(username) if username
                else {}
            )

            p = subprocess.Popen(
                ' '.join(command_arr),
                shell=True,
                stdout=subprocess.PIPE if consumer else None,
                **profile
            )

            result = p.communicate()
            return consumer(result) if consumer else None
        
        return wrapper
    return wrapper_factory

@command()
def bash(args: list):
    return args

@command()
def pip_install(packages: list):
    return [sys.executable, "-m", "pip", "install", "--user", "--no-cache-dir"] + packages

@command()
def python3(script: list):
    return [sys.executable, "-c", f"'{';'.join(script)}'"]
