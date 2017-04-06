#!/bin/bash

USAGE="USAGE: . install_tethys.sh [options]\n
\n
OPTIONS:\n
    -t, --tethys-home <PATH>            path for tethys home directory. Default is /usr/lib/tethys on Linux and /Library/Applicaiton/tethys on Mac OS.\n
    -a, --allowed-host <HOST>           hostname or IP address on which to server tethys. Default is 127.0.0.1.\n
    -p, --port <PORT>                   port on which to server tethys. Default is 8000 on Linux and 8001 on Mac OS.\n
    -b, --branch <BRANCH_NAME>          repository branch to checkout. Default is 'dev'.\n
    -c, --conda-home <PATH>             path to conda home directory. Default is \${TETHYS_HOME}/miniconda.\n
    --db-username <USERNAME>            username that the tethys database server will use. Default is 'tethys_default'.\n
    --db-password <PASSWORD>            password that the tethys database server will use. Default is 'pass'.\n
    --db-port <PORT>                    port that the tethys database server will use. Default is 5436.\n
    -S, --superuser <USERNAME>          Tethys super user name. Default is 'admin'.\n
    -E, --superuser-email <EMAIL>       Tethys super user email. Default is ''.\n
    -P, --superuser-pass <PASSWORD>     Tethys super user password. Default is 'pass'.\n
    --install-docker                    Flag to include Docker installation as part of the install script (Ubuntu only).\n
    --docker-options <OPTIONS>          Command line options to pass to the `tethys docker init` call if --install-docker is used. Default is '-d'.\n
    -x                                  Flag to turn on shell command echoing.\n
    -h, --help                          Print this help information.\n
"

print_usage ()
{
    echo -e ${USAGE}
    exit
}
set -e  # exit on error

# Set platform specific default options
if [ "$(uname)" = "Linux" ]
then
    TETHYS_HOME="/usr/lib/tethys"
    MINICONDA_URL="wget https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh -O"
    BASH_PROFILE=".bashrc"
    TETHYS_PORT=8000
elif [ "$(uname)" = "Darwin" ]  # i.e. MacOSX
then
    TETHYS_HOME="/Library/Application/tethys"
    MINICONDA_URL="curl https://repo.continuum.io/miniconda/Miniconda3-latest-MacOSX-x86_64.sh -o"
    BASH_PROFILE=".bash_profile"
    TETHYS_PORT=8001
else
    echo $(uname) is not a supported operating system.
    exit
fi

# Set default options
ALLOWED_HOST='127.0.0.1'
TETHYS_DB_USERNAME='tethys_default'
TETHYS_DB_PASSWORD='pass'
TETHYS_DB_PORT=5436
BRANCH=dev

TETHYS_SUPER_USER='admin'
TETHYS_SUPER_USER_EMAIL=''
TETHYS_SUPER_USER_PASS='pass'

DOCKER_OPTIONS='-d'

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
    -a|--allowed-host)
    set_option_value ALLOWED_HOST "$2"
    shift # past argument
    ;;
    -p|--port)
    set_option_value TETHYS_PORT "$2"
    shift # past argument
    ;;
    -b|--branch)
    set_option_value BRANCH "$2"
    shift # past argument
    ;;
    -c|--conda-home)
    set_option_value CONDA_HOME "$2"
    shift # past argument
    ;;
    --db-username)
    set_option_value TETHYS_DB_USERNAME "$2"
    shift # past argument
    ;;
    --db-password)
    set_option_value TETHYS_DB_PASS "$2"
    shift # past argument
    ;;
    --db-port)
    set_option_value TETHYS_DB_PORT "$2"
    shift # past argument
    ;;
    -S|--superuser)
    set_option_value TETHYS_SUPER_USER "$2"
    shift # past argument
    ;;
    -E|--superuser-email)
    set_option_value TETHYS_SUPER_USER_EMAIL "$2"
    shift # past argument
    ;;
    -P|--superuser-pass)
    set_option_value TETHYS_SUPER_USER_PASS "$2"
    shift # past argument
    ;;
    --docker-options)
    set_option_value DOCKER_OPTIONS "$2"
    shift # past argument
    ;;
    --install-docker)
    if [ "$(uname)" = "Linux" ]
    then
        INSTALL_DOCKER="true"
    else
        echo Automatic installation of Docker is not supported on $(uname). Ignoring option $key.
    fi
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

# set CONDA_HOME relative to TETHYS_HOME if not already set
if [ -z ${CONDA_HOME} ]
then
    CONDA_HOME="${TETHYS_HOME}/miniconda"
fi

if [ -n "${ECHO_COMMANDS}" ]
then
    set -x # echo commands as they are executed
fi

# prompt for sudo
echo "Tethys installation requires some commands to be run with sudo. Please enter password:"
sudo echo "Starting Tethys Installation..."

sudo mkdir -p ${TETHYS_HOME}
sudo chown ${USER} ${TETHYS_HOME}

# install miniconda
${MINICONDA_URL} "${TETHYS_HOME}/miniconda.sh"
sudo bash "${TETHYS_HOME}/miniconda.sh" -b -p "${CONDA_HOME}"
sudo chmod -R o+w "${CONDA_HOME}"
export PATH="${CONDA_HOME}/bin:$PATH"

# clone Tethys repo
conda install --yes git
git clone https://github.com/sdc50/tethys.git "${TETHYS_HOME}/src"
cd "${TETHYS_HOME}/src"
git checkout ${BRANCH}

# create conda env and install Tethys
conda env create -f environment_py2.yml
. activate tethys
python setup.py develop
tethys gen settings -d "${TETHYS_HOME}/src/tethys_apps" --allowed-host ${ALLOWED_HOST} --db-username ${TETHYS_DB_USERNAME} --db-password ${TETHYS_DB_PASSWORD} --db-port ${TETHYS_DB_PORT}

# Setup local database
initdb  -U postgres -D "${TETHYS_HOME}/psql/data"
pg_ctl -U postgres -D "${TETHYS_HOME}/psql/data" -l "${TETHYS_HOME}/psql/logfile" start -o "-p ${TETHYS_DB_PORT}"
echo "wating for databases to startup..."; sleep 10
psql -U postgres -p ${TETHYS_DB_PORT} --command "CREATE USER ${TETHYS_DB_USERNAME} WITH NOCREATEDB NOCREATEROLE NOSUPERUSER PASSWORD '${TETHYS_DB_PASSWORD}';"
createdb -U postgres -p ${TETHYS_DB_PORT} -O ${TETHYS_DB_USERNAME} ${TETHYS_DB_USERNAME} -E utf-8 -T template0

# Initialze Tethys database
tethys manage syncdb
echo "from django.contrib.auth.models import User; User.objects.create_superuser('${TETHYS_SUPER_USER}', '${TETHYS_SUPER_USER_EMAIL}', '${TETHYS_SUPER_USER_PASS}')" | python manage.py shell

# setup shortcuts and aliases
ACTIVATE_DIR="${CONDA_HOME}/envs/tethys/etc/conda/activate.d"
DEACTIVATE_DIR="${CONDA_HOME}/envs/tethys/etc/conda/deactivate.d"
mkdir -p ${ACTIVATE_DIR} ${DEACTIVATE_DIR}
ACTIVATE_SCRIPT="${ACTIVATE_DIR}/tethys-activate.sh"
DEACTIVATE_SCRIPT="${DEACTIVATE_DIR}/tethys-deactivate.sh"

echo "export TETHYS_HOME='${TETHYS_HOME}'" >> ${ACTIVATE_SCRIPT}
echo "export TETHYS_PORT='${TETHYS_PORT}'" >> ${ACTIVATE_SCRIPT}
echo "export TETHYS_DB_PORT='${TETHYS_DB_PORT}'" >> ${ACTIVATE_SCRIPT}
echo "alias tethys_start_db='pg_ctl -U postgres -D \${TETHYS_HOME}/psql/data -l \${TETHYS_HOME}/psql/logfile start -o \"-p \${TETHYS_DB_PORT}\"'" >> ${ACTIVATE_SCRIPT}
echo "alias tstartdb=tethys_start_db" >> ${ACTIVATE_SCRIPT}
echo "alias tethys_stop_db='pg_ctl -U postgres -D \${TETHYS_HOME}/psql/data stop'" >> ${ACTIVATE_SCRIPT}
echo "alias tstopdb=tethys_stop_db" >> ${ACTIVATE_SCRIPT}
echo "alias tms='tethys manage start -p ${ALLOWED_HOST}:\${TETHYS_PORT}'" >> ${ACTIVATE_SCRIPT}

. ${ACTIVATE_SCRIPT}

echo "unset TETHYS_HOME" >> ${DEACTIVATE_SCRIPT}
echo "unset TETHYS_PORT" >> ${DEACTIVATE_SCRIPT}
echo "unset TETHYS_DB_PORT" >> ${DEACTIVATE_SCRIPT}
echo "unalias tethys_start_db" >> ${DEACTIVATE_SCRIPT}
echo "unalias tstartdb" >> ${DEACTIVATE_SCRIPT}
echo "unalias tethys_stop_db" >> ${DEACTIVATE_SCRIPT}
echo "unalias tstopdb" >> ${DEACTIVATE_SCRIPT}
echo "unalias tms" >> ${DEACTIVATE_SCRIPT}

echo "# Tethys Platform" >> ~/${BASH_PROFILE}
echo "alias t='. ${CONDA_HOME}/bin/activate tethys'" >> ~/${BASH_PROFILE}

echo "Tethys installation complete!"

# Install Docker (if flag is set)
set +e  # don't exit on error anymore

if [ "$(uname)" = "Linux" -a "${INSTALL_DOCKER}" = "true" ]
then
    echo "Installing Docker..."
    . activate tethys # activate tethys environment
    sudo apt-key adv --keyserver hkp://p80.pool.sks-keyservers.net:80 --recv-keys 58118E89F3A912897C070ADBF76221572C52609D
    echo "deb https://apt.dockerproject.org/repo ubuntu-$(lsb_release -c | awk '{print $2}') main" | sudo tee /etc/apt/sources.list.d/docker.list
    sudo apt-get update
    sudo apt-get install -y docker-engine
    sudo gpasswd -a ${USER} docker
    sudo service docker restart
    sg docker -c "tethys docker init ${DOCKER_OPTIONS}"
    set +x
    echo "Docker installation finished!"
    echo "You must re-login for Docker permissions to be activated."
    echo "(Alternatively you can run `newgrp docker`)"
fi

# execute profile to activate new alias
set +x
. ~/${BASH_PROFILE}