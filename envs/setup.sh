DIR=$( dirname "${BASH_SOURCE[0]}" )

for arg in "$@"
do
    case $arg in
        -s|--server-type)
        SERVER_TYPE=$2
        shift
        shift
        ;;
    esac
done

python3 -m pip install $DIR/../sagesaver-core --user

case $SERVER_TYPE in
    mongo)
    . $DIR/mongo/setup.sh "$@"
    ;;
    mysql)
    . $DIR/mysql/setup.sh "$@"
    ;;
    notebook)
    su ec2-user -c "python3 -m pip install $DIR/../sagesaver-core --user"
    . $DIR/notebook/setup.sh "$@"
    ;;
esac