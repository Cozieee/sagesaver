ANACONDA_PATH="/opt/anaconda3"
CONDA=$ANACONDA_PATH/bin/conda

wget https://repo.anaconda.com/archive/Anaconda3-2020.11-Linux-x86_64.sh -O anaconda3.sh
bash anaconda3.sh -b -p $ANACONDA_PATH
rm -f anaconda3.sh

$CONDA init bash
su - ec2-user -c "$CONDA init bash"

ln -s $ANACONDA_PATH /root/
ln -s $ANACONDA_PATH /home/ec2-user/