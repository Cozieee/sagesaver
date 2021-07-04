cd "$( dirname "${BASH_SOURCE[0]}" )"

truncate --no-create -s 0 *.log

SAGESAVER_PATH=$(pwd)
echo "* * * * * cd $SAGESAVER_PATH && root-env/bin/python3 autostop.py >> autostop.log 2>&1" | crontab -