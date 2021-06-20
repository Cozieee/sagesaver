cd "$( dirname "${BASH_SOURCE[0]}" )"

function render_template() {
  eval "echo \"$(cat $1)\""
}

for arg in "$@"
do
    case $arg in
        -p|--password)
        MONGO_PWD=$2
        shift
        shift
        ;;
    esac
done

python3 -m venv ../root-env
source ../root-env/bin/activate
pip3 install -r requirements_root.txt
deactivate

cp ./mongodb-org-4.4.repo /etc/yum.repos.d/
yum -y install mongodb-org

mkfs.xfs -L mongodata /dev/sdf
mkfs.xfs -L mongojournal /dev/sdg
mkfs.xfs -L mongolog /dev/sdh

mkdir /data
mkdir /journal
mkdir /log

mount -t xfs /dev/sdf /data
mount -t xfs /dev/sdg /journal
mount -t xfs /dev/sdh /log

ln -s /journal /data/journal

chown mongod:mongod /data
chown mongod:mongod /log/
chown mongod:mongod /journal/

cat >> /etc/fstab <<EOF
/dev/sdf /data    xfs defaults,auto,noatime,noexec 0 0
/dev/sdg /journal xfs defaults,auto,noatime,noexec 0 0
/dev/sdh /log     xfs defaults,auto,noatime,noexec 0 0
EOF

cat >> /etc/security/limits.conf <<EOF
* soft nofile 64000
* hard nofile 64000
* soft nproc 32000
* hard nproc 32000
EOF

cat >> /etc/security/limits.d/90-nproc.conf <<EOF
* soft nproc 32000
* hard nproc 32000
EOF

cp ./disable-transparent-hugepages /etc/init.d/
chmod 755 /etc/init.d/disable-transparent-hugepages
cp ./logrotate-mongodb /etc/logrotate.d/mongodb

AUTHORIZATION=disabled
render_template ./mongod.conf.tmpl > /etc/mongod.conf

chkconfig mongod on
service mongod start

mongo <<EOF
use admin
db.createUser({ user: "admin", pwd: "${MONGO_PWD}", roles: ["root"] })
EOF

AUTHORIZATION=enabled
render_template ./mongod.conf.tmpl > /etc/mongod.conf

service mongod restart