# Required: -p [Jupyter Password]
# Optional: -h [Jupyter Port Number]

cd "$( dirname "${BASH_SOURCE[0]}" )"

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

python3 -m venv ../venv
source ../venv/bin/activate
pip3 install -r ../requirements.txt

JPY_SHA=$(
python3 - <<-EOF
from IPython.lib import passwd
print(passwd('$JPY_PWD'))
EOF
)

render_template jupyter_lab_config.py.tmpl \
    > ../venv/etc/jupyter/jupyter_lab_config.py