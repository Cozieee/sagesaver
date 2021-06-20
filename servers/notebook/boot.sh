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
screen -dm bash -c "jupyter lab --allow-root 2>&1 | tee -a jupyter.log; exec sh"

SAGESAVER_PATH=$(pwd)
echo "* * * * * cd $SAGESAVER_PATH && venv/bin/python3 autostop.py >> autostop.log 2>&1" | crontab -