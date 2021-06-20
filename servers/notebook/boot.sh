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

source venv/bin/activate
truncate -s 0 *.log
python3 db_boot.py

SAGESAVER_PATH=$(pwd)

screen -dm bash -c '
cd $JPY_CWD_PATH
jupyter lab --allow-root 2>&1 | tee -a $SAGESAVER_PATH/jupyter.log
exec sh
'

echo "* * * * * cd $SAGESAVER_PATH && venv/bin/python3 autostop.py >> autostop.log 2>&1" | crontab -