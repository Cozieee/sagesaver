cd "$( dirname "${BASH_SOURCE[0]}" )"

for arg in "$@"
do
    case $arg in
        -j|--jupyter)
        JPY_CWD_PATH=$2
        shift
        shift
        ;;
    esac
done

source root-env/bin/activate
truncate --no-create -s 0 *.log
python3 db_boot.py

sudo -u ec2-user screen -dm bash -c "
source ~/notebook-env/bin/activate
cd $JPY_CWD_PATH
jupyter lab --collaborative 2>&1 | tee -a ~/jupyter.log
exec sh
"

SAGESAVER_PATH=$(pwd)
echo "* * * * * cd $SAGESAVER_PATH && root-env/bin/python3 autostop.py >> autostop.log 2>&1" | crontab -