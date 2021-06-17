# Requirements:
# - Anaconda3 is installed
# - Run as root

# Required: -p [Jupyter Password]
# Optional: -h [Jupyter Port Number]

# ANACONDA_PATH=${ANACONDA_PATH:-"/root/anaconda3"}

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

#$BIN/conda install -y -c conda-forge jmespath
python3 -m venv ../venv
source ../venv/bin/activate
pip3 install -r ../requirements.txt

JPY_CONFIG=$ANACONDA_PATH/etc/jupyter
JPY_SHA=$(
python - <<-EOF
    from IPython.lib import passwd
    print(passwd('$JPY_PWD'))
EOF
)

render_template ./jupyter_notebook_config.py.tmpl \
    > $JPY_CONFIG/jupyter_notebook_config.py