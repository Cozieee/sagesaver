cd "$( dirname "${BASH_SOURCE[0]}" )"

function render_template() {
  eval "echo \"$(cat $1)\""
}

for arg in "$@"
do
    case $arg in
        -u|--username)
        DB_USER=$2
        shift
        shift
        ;;
        -p|--password)
        DB_PWD=$2
        shift
        shift
        ;;
    esac
done

rpm -Uvh https://dev.mysql.com/get/mysql57-community-release-el7-11.noarch.rpm 
yum install -y mysql-community-server
systemctl enable mysqld
systemctl start mysqld

TMP_PWD=$(echo $(grep 'temporary password' /var/log/mysqld.log)\
    | rev | cut -d ' ' -f 1 | rev)

mysqladmin --user=root --password=$TMP_PWD password $DB_PWD

mysql --user=root --password=$DB_PWD --execute="
RENAME USER 'root'@'localhost' TO '$DB_USER'@'%';
FLUSH PRIVILEGES;
"

mysql --user=$DB_USER --password=$DB_PWD --execute="
SET GLOBAL log_output = 'FILE';
SET GLOBAL general_log_file = '/var/log/sagesaver/mysql.log';
SET GLOBAL general_log = 'ON';
"