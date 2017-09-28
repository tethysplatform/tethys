#!/bin/bash

USAGE="USAGE: . install_tethys.sh [options]\n
\n
OPTIONS:\n
    -t, --tethys-home <PATH>            Path for tethys home directory. Default is ~/tethys.\n
    --python-version <PYTHON_VERSION>   Main python version to install tethys environment into (2 or 3). Default is 2.\n
    -x                                  Flag to turn on shell command echoing.\n
    -h, --help                          Print this help information.\n
"

print_usage ()
{
    echo -e ${USAGE}
    exit
}
set -e  # exit on error
LINUX_DISTRIBUTION=$(lsb_release -is) || LINUX_DISTRIBUTION=$(python -c "import platform; print(platform.linux_distribution(full_distribution_name=0)[0])")
# convert to lower case
LINUX_DISTRIBUTION=${LINUX_DISTRIBUTION,,}
MINICONDA_URL="https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh"
BASH_PROFILE=".bashrc"
resolve_relative_path ()
{
    local __path_var="$1"
    eval $__path_var="'$(readlink -f $2)'"
}

# Set default options
TETHYS_HOME=~/tethys
TETHYS_PORT=80
CONDA_ENV_NAME='tethys'
PYTHON_VERSION='2'


# parse command line options
set_option_value ()
{
    local __option_key="$1"
    value="$2"
    if [[ $value == -* ]]
    then
        print_usage
    fi
    eval $__option_key="$value"
}
while [[ $# -gt 0 ]]
do
key="$1"

case $key in
    -t|--tethys-home)
    set_option_value TETHYS_HOME "$2"
    shift # past argument
    ;;
    -n|--conda-env-name)
    set_option_value CONDA_ENV_NAME "$2"
    shift # past argument
    ;;
    --python-version)
    set_option_value PYTHON_VERSION "$2"
    shift # past argument
    ;;
    -x)
    ECHO_COMMANDS="true"
    ;;
    -h|--help)
    print_usage
    ;;
    *) # unknown option
    echo Ignoring unrecognized option: $key
    ;;
esac
shift # past argument or value
done

# resolve relative paths
CONDA_HOME="${TETHYS_HOME}/miniconda"
resolve_relative_path TETHYS_HOME ${TETHYS_HOME}
resolve_relative_path CONDA_HOME ${CONDA_HOME}



if [ -n "${ECHO_COMMANDS}" ]
then
    set -x # echo commands as they are executed
fi


# Set paths for environment activate/deactivate scripts
ACTIVATE_DIR="${CONDA_HOME}/envs/${CONDA_ENV_NAME}/etc/conda/activate.d"
DEACTIVATE_DIR="${CONDA_HOME}/envs/${CONDA_ENV_NAME}/etc/conda/deactivate.d"
ACTIVATE_SCRIPT="${ACTIVATE_DIR}/tethys-activate.sh"
DEACTIVATE_SCRIPT="${DEACTIVATE_DIR}/tethys-deactivate.sh"


echo "Starting Tethys Installation..."

mkdir -p "${TETHYS_HOME}"

# Install Miniconda
echo "Installing Miniconda..."
wget ${MINICONDA_URL} -O "${TETHYS_HOME}/miniconda.sh" || (echo -using curl instead; curl ${MINICONDA_URL} -o "${TETHYS_HOME}/miniconda.sh")
pushd ./
cd "${TETHYS_HOME}"
bash miniconda.sh -b -p "${CONDA_HOME}"
popd

export PATH="${CONDA_HOME}/bin:$PATH"

cd "${TETHYS_HOME}/src"

# create conda env and install Tethys
echo "Setting up the ${CONDA_ENV_NAME} environment..."
conda env create -n ${CONDA_ENV_NAME} -f "environment_py${PYTHON_VERSION}.yml"
. activate ${CONDA_ENV_NAME}

python setup.py develop

set +e  # don't exit on error anymore

# Rename some variables for reference after deactivating tethys environment.
TETHYS_CONDA_HOME=${CONDA_HOME}
TETHYS_CONDA_ENV_NAME=${CONDA_ENV_NAME}

on_exit(){
    set +e
    set +x
}
trap on_exit EXIT
