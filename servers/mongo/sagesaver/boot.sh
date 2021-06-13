truncate -s 0 $1/*.log;
echo "* * * * * cd $1 && ipython autostop.py >> autostop.log 2>&1" | crontab -