truncate -s 0 $1/*.log;
ipython $1/db_boot.py;
screen -dm bash -c "cd $2; jupyter lab --allow-root 2>&1 | tee -a $1/jupyter.log; exec sh";
echo "* * * * * cd $1 && ipython autostop.py >> autostop.log 2>&1" | crontab -;