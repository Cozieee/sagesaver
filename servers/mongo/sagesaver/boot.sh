CFG=${SAGESAVER_CONFIG_PATH:-"/etc/sagesaver/config.json"}

SAGESAVER_PATH=$(jq -r .paths.sagesaver $CFG)

truncate -s 0 $SAGESAVER_PATH/*.log;
echo "* * * * * cd $SAGESAVER_PATH && python autostop.py >> autostop.log 2>&1" | crontab -