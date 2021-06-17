# Requirements:
# - Anaconda3 is installed

CFG=${SAGESAVER_CONFIG_PATH:-"/etc/sagesaver/config.json"}

# ANACONDA_PATH=$(jq -r .paths.anaconda $CFG)

SAGESAVER_PATH=$(jq -r .paths.sagesaver $CFG)
JUPYTER_CWD_PATH=$(jq -r .paths.jupyter_cwd $CFG)

truncate -s 0 $SAGESAVER_PATH/*.log;

# $BIN/python $SAGESAVER_PATH/db_boot.py;
# screen -dm bash -c "cd $JUPYTER_APP_PATH; $BIN/jupyter lab --allow-root 2>&1 | tee -a $SAGESAVER_PATH/jupyter.log; exec sh";
# echo "* * * * * cd $SAGESAVER_PATH && $BIN/python autostop.py >> $SAGESAVER_PATH/autostop.log 2>&1" | crontab -;
python $SAGESAVER_PATH/db_boot.py;
screen -dm bash -c "cd $JUPYTER_APP_PATH; jupyter lab --allow-root 2>&1 | tee -a $SAGESAVER_PATH/jupyter.log; exec sh";
echo "* * * * * cd $SAGESAVER_PATH && python autostop.py >> $SAGESAVER_PATH/autostop.log 2>&1" | crontab -;