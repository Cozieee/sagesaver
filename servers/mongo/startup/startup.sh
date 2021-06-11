> /home/ec2-user/startup/mongo.log
> /home/ec2-user/startup/autostop.log

echo "* * * * * /home/ec2-user/miniconda3/bin/ipython -c '\%run /home/ec2-user/startup/autostop.py /home/ec2-user/startup/mongo.log -t 1800' >> /home/ec2-user/startup/autostop.log 2>&1" | crontab -
