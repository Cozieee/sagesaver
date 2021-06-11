> /home/ec2-user/startup/autostop.log

/home/ec2-user/anaconda3/bin/ipython startup/db_boot.py

screen -dm bash -c "cd /home/ec2-user/efs; jupyter lab 2>&1 | tee -a /home/ec2-user/startup/jupyter.log; exec sh"

echo "* * * * * /home/ec2-user/anaconda3/bin/ipython /home/ec2-user/startup/autostop.py >> /home/ec2-user/startup/autostop.log 2>&1" | crontab -
