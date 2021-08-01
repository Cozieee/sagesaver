import sys
import os
import pwd

def install(packages):
    return [sys.executable, "-m", "pip", "install"] + packages + ["--user"]


def demote(username):
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