# Required: -p [Jupyter Password]
# Optional: -h [Jupyter Port Number]

DIR=$( dirname "${BASH_SOURCE[0]}" )

function render_template() {
  eval "echo \"$(cat $1)\""
}

JPY_PORT=8888
for arg in "$@"
do
    case $arg in
        -p|--password)
        JPY_PWD=$2
        shift
        shift
        ;;
        --port)
        JPY_PORT=$2
        shift
        shift
        ;;
    esac
done

pip3 install -r $DIR/requirements_root.txt

JPY_SHA=$(
python3 - <<-EOF
from IPython.lib import passwd
print(passwd('$JPY_PWD'))
EOF
)

mkdir /home/ec2-user/.jupyter
render_template $DIR/jupyter_lab_config.py.tmpl \
    > /home/ec2-user/.jupyter/jupyter_lab_config.py

su ec2-user
pip3 install -r $DIR/requirements_notebook.txt
sudo su