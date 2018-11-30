#!/bin/bash

RED=`tput setaf 1`
GREEN=`tput setaf 2`
YELLOW=`tput setaf 3`
RESET_COLOR=`tput sgr0`

USAGE="USAGE: . install_tethys.sh [options]\n
\n
OPTIONS:\n
\t    -t, --tethys-home <PATH>            \t\t Path for tethys home directory. Default is ~/tethys.\n
\t    -a, --allowed-host <HOST>           \t\t Hostname or IP address on which to serve tethys. Default is 127.0.0.1.\n
\t    -p, --port <PORT>                   \t\t\t Port on which to serve tethys. Default is 8000.\n
\t    -b, --branch <BRANCH_NAME>          \t\t Branch to checkout from version control. Default is 'release'.\n
\t    -c, --conda-home <PATH>             \t\t Path where Miniconda will be installed, or to an existing installation of Miniconda. Default is \${TETHYS_HOME}/miniconda.\n
\t    -n, --conda-env-name <NAME>         \t\t Name for tethys conda environment. Default is 'tethys'.\n
\t    --python-version <PYTHON_VERSION>   \t Main python version to install tethys environment into (2-deprecated or 3). Default is 3.\n
\t    --db-username <USERNAME>            \t\t Username that the tethys database server will use. Default is 'tethys_default'.\n
\t    --db-password <PASSWORD>            \t\t Password that the tethys database server will use. Default is 'pass'.\n
\t    --db-super-username <USERNAME>      \t Username for super user on the tethys database server. Default is 'tethys_super'.\n
\t    --db-super-password <PASSWORD>      \t Password for super user on the tethys database server. Default is 'pass'.\n
\t    --db-port <PORT>                    \t\t\t Port that the tethys database server will use. Default is 5436.\n
\t    --db-dir <PATH>                     \t\t\t Path where the local PostgreSQL database will be created. Default is \${TETHYS_HOME}/psql.\n
\t    -S, --superuser <USERNAME>          \t\t Tethys super user name. Default is 'admin'.\n
\t    -E, --superuser-email <EMAIL>       \t\t Tethys super user email. Default is ''.\n
\t    -P, --superuser-pass <PASSWORD>     \t Tethys super user password. Default is 'pass'.\n
\t    --skip-tethys-install               \t\t\t Flag to skip the Tethys installation so that the Docker installation or production installation can be added to an existing Tethys installation.\n
\t    --partial-tethys-install <FLAGS>    \t List of flags to indicate which steps of the installation to do (e.g. --partial-tethys-install mresdat).\n\n

\t        \t FLAGS:\n
\t        \t\t m - Install Miniconda\n
\t        \t\t r - Clone Tethys repository\n
\t        \t\t e - Create Conda environment\n
\t        \t\t s - Create 'settings.py' file\n
\t        \t\t d - Setup local database server\n
\t        \t\t i - Initialize database server with Tethys database and superuser\n
\t        \t\t a - Create activation/deactivation scripts for the Tethys Conda environment\n
\t        \t\t t - Create the 't' alias t\n\n

\t        \t NOTE: if --skip-tethys-install is used then this option will be ignored.\n\n

\t    --install-docker                    \t\t\t Flag to include Docker installation as part of the install script (Linux only).\n
\t    --docker-options <OPTIONS>          \t\t Command line options to pass to the 'tethys docker init' call if --install-docker is used. Default is \"'-d'\".\n
\t    --production                        \t\t\t\t Flag to install Tethys in a production configuration.\n
\t    --configure-selinux                 \t\t\t Flag to perform configuration of SELinux for production installation. (Linux only).\n
\t    -x                                  \t\t\t\t\t Flag to turn on shell command echoing.\n
\t    -h, --help                          \t\t\t\t Print this help information.\n
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
elif [ "$(uname)" = "Darwin" ]  # i.e. MacOSX
then
    MINICONDA_URL="https://repo.continuum.io/miniconda/Miniconda3-latest-MacOSX-x86_64.sh"
    BASH_PROFILE=".bash_profile"
    resolve_relative_path ()
    {
        local __path_var="$1"
        eval $__path_var="'$(python -c "import os; print(os.path.abspath('$2'))")'"
    }
else
    echo $(uname) is not a supported operating system.
    exit
fi

# Set default options
ALLOWED_HOST='127.0.0.1'
TETHYS_HOME=~/tethys
TETHYS_PORT=8000
TETHYS_DB_USERNAME='tethys_default'
TETHYS_DB_PASSWORD='pass'
TETHYS_DB_SUPER_USERNAME='tethys_super'
TETHYS_DB_SUPER_PASSWORD='pass'
TETHYS_DB_PORT=5436
CONDA_ENV_NAME='tethys'
PYTHON_VERSION='3'
BRANCH='release'

TETHYS_SUPER_USER='admin'
TETHYS_SUPER_USER_EMAIL=''
TETHYS_SUPER_USER_PASS='pass'

DOCKER_OPTIONS='-d'

INSTALL_MINICONDA="true"
CLONE_REPO="true"
CREATE_ENV="true"
CREATE_SETTINGS="true"
SETUP_DB="true"
CREATE_ENV_SCRIPTS="true"
CREATE_SHORTCUTS="true"

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
    -n|--conda-env-name)
    set_option_value CONDA_ENV_NAME "$2"
    shift # past argument
    ;;
    --python-version)
    set_option_value PYTHON_VERSION "$2"
    shift # past argument
    ;;
    --db-username)
    set_option_value TETHYS_DB_USERNAME "$2"
    shift # past argument
    ;;
    --db-password)
    set_option_value TETHYS_DB_PASSWORD "$2"
    shift # past argument
    ;;
    --db-super-username)
    set_option_value TETHYS_DB_SUPER_USERNAME "$2"
    shift # past argument
    ;;
    --db-super-password)
    set_option_value TETHYS_DB_SUPER_PASSWORD "$2"
    shift # past argument
    ;;
    --db-port)
    set_option_value TETHYS_DB_PORT "$2"
    shift # past argument
    ;;
    --db-dir)
    set_option_value TETHYS_DB_DIR "$2"
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
    --skip-tethys-install)
        SKIP_TETHYS_INSTALL="true"
    ;;
    --partial-tethys-install)
        # Set all steps to false be default and then activate only those steps that have been specified.
        INSTALL_MINICONDA=
        CLONE_REPO=
        CREATE_ENV=
        CREATE_SETTINGS=
        SETUP_DB=
        INITIALIZE_DB=
        CREATE_ENV_SCRIPTS=
        CREATE_SHORTCUTS=

        if [[ "$2" = *"m"* ]]; then
            INSTALL_MINICONDA="true"
        fi
        if [[ "$2" = *"r"* ]]; then
            CLONE_REPO="true"
        fi
        if [[ "$2" = *"e"* ]]; then
            CREATE_ENV="true"
        fi
        if [[ "$2" = *"s"* ]]; then
            CREATE_SETTINGS="true"
        fi
        if [[ "$2" = *"d"* ]]; then
            SETUP_DB="true"
        fi
        if [[ "$2" = *"i"* ]]; then
            INITIALIZE_DB="true"
        fi
        if [[ "$2" = *"a"* ]]; then
            CREATE_ENV_SCRIPTS="true"
        fi
        if [[ "$2" = *"t"* ]]; then
            CREATE_SHORTCUTS="true"
        fi
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
    --docker-options)
    set_option_value DOCKER_OPTIONS "$2"
    shift # past argument
    ;;
    --production)
    if [ "$(uname)" = "Linux" ]
    then
        PRODUCTION="true"
    else
        echo Automatic production installation is not supported on $(uname). Ignoring option $key.
    fi
    ;;
    --configure-selinux)
    if [ "$(uname)" = "Linux" ]
    then
        SELINUX="true"
    else
        echo SELinux confiuration is not supported on $(uname). Ignoring option $key.
    fi
    ;;
    -x)
    ECHO_COMMANDS="true"
    ;;
    -h|--help)
    print_usage
    ;;
    *) # unknown option
    echo Unrecognized option: $key
    print_usage
    ;;
esac
shift # past argument or value
done

# resolve relative paths
resolve_relative_path TETHYS_HOME ${TETHYS_HOME}

# set CONDA_HOME relative to TETHYS_HOME if not already set
if [ -z "${CONDA_HOME}" ]
then
    CONDA_HOME="${TETHYS_HOME}/miniconda"
else
    resolve_relative_path CONDA_HOME ${CONDA_HOME}
fi

# set TETHYS_DB_DIR relative to TETHYS_HOME if not already set
if [ -z "${TETHYS_DB_DIR}" ]
then
    TETHYS_DB_DIR="${TETHYS_HOME}/psql"
else
    resolve_relative_path TETHYS_DB_DIR ${TETHYS_DB_DIR}
fi

if [ -n "${ECHO_COMMANDS}" ]
then
    set -x # echo commands as they are executed
fi

# Set paths for environment activate/deactivate scripts
ACTIVATE_DIR="${CONDA_HOME}/envs/${CONDA_ENV_NAME}/etc/conda/activate.d"
DEACTIVATE_DIR="${CONDA_HOME}/envs/${CONDA_ENV_NAME}/etc/conda/deactivate.d"
ACTIVATE_SCRIPT="${ACTIVATE_DIR}/tethys-activate.sh"
DEACTIVATE_SCRIPT="${DEACTIVATE_DIR}/tethys-deactivate.sh"


if [ -z "${SKIP_TETHYS_INSTALL}" ]
then
    echo "Starting Tethys Installation..."

    mkdir -p "${TETHYS_HOME}"

    if [ -n "${INSTALL_MINICONDA}" ]
    then
        echo "MINICONDA" ${INSTALL_MINICONDA}
        # install miniconda
        # first see if Miniconda is already installed
        if [ -f "${CONDA_HOME}/bin/activate" ]
        then
            echo "Using existing Miniconda installation..."
        else
            echo "Installing Miniconda..."
            wget ${MINICONDA_URL} -O "${TETHYS_HOME}/miniconda.sh" || (echo -using curl instead; curl ${MINICONDA_URL} -o "${TETHYS_HOME}/miniconda.sh")
            pushd ./
            cd "${TETHYS_HOME}"
            bash miniconda.sh -b -p "${CONDA_HOME}"
            popd
        fi
    fi

    source "${CONDA_HOME}/etc/profile.d/conda.sh"

    if [ -n "${CLONE_REPO}" ]
    then
        # clone Tethys repo
        echo "Cloning the Tethys Platform repo..."
        conda install --yes git
        git clone https://github.com/tethysplatform/tethys.git "${TETHYS_HOME}/src"
        cd "${TETHYS_HOME}/src"
        git checkout ${BRANCH}
    fi

    if [ -n "${CREATE_ENV}" ]
    then
        # create conda env and install Tethys
        echo "Setting up the ${CONDA_ENV_NAME} environment..."
        if [ "${PYTHON_VERSION}" == "2" ]
        then
            echo "${YELLOW}WARNING: Support for Python 2 is deprecated and will be removed in Tethys version 3.${RESET_COLOR}"
        fi
        conda env create -n ${CONDA_ENV_NAME} -f "${TETHYS_HOME}/src/environment_py${PYTHON_VERSION}.yml"
        conda activate ${CONDA_ENV_NAME}
        python "${TETHYS_HOME}/src/setup.py" develop
    else
        echo "Activating the ${CONDA_ENV_NAME} environment..."
        conda activate ${CONDA_ENV_NAME}
    fi

    if [ -n "${CREATE_SETTINGS}" ]
    then
        # only pass --allowed-hosts option to gen settings command if it is not the default
        if [ ${ALLOWED_HOST} != "127.0.0.1" ]
        then
            ALLOWED_HOST_OPT="--allowed-host ${ALLOWED_HOST}"
        fi
        tethys gen settings ${ALLOWED_HOST_OPT} --db-username ${TETHYS_DB_USERNAME} --db-password ${TETHYS_DB_PASSWORD} --db-port ${TETHYS_DB_PORT}
    fi

    if [ -n "${SETUP_DB}" ]
    then
        # Setup local database
        export TETHYS_DB_PORT="${TETHYS_DB_PORT}"
        echo ${TETHYS_DB_PORT}
        echo "Setting up the Tethys database..."
        initdb  -U postgres -D "${TETHYS_DB_DIR}/data"
        pg_ctl -U postgres -D "${TETHYS_DB_DIR}/data" -l "${TETHYS_DB_DIR}/logfile" start -o "-p ${TETHYS_DB_PORT}"
        echo "Waiting for databases to startup..."; sleep 10
        psql -U postgres -p ${TETHYS_DB_PORT} --command "CREATE USER ${TETHYS_DB_USERNAME} WITH NOCREATEDB NOCREATEROLE NOSUPERUSER PASSWORD '${TETHYS_DB_PASSWORD}';"
        createdb -U postgres -p ${TETHYS_DB_PORT} -O ${TETHYS_DB_USERNAME} ${TETHYS_DB_USERNAME} -E utf-8 -T template0
        psql -U postgres -p ${TETHYS_DB_PORT} --command "CREATE USER ${TETHYS_DB_SUPER_USERNAME} WITH CREATEDB NOCREATEROLE SUPERUSER PASSWORD '${TETHYS_DB_SUPER_PASSWORD}';"
        createdb -U postgres -p ${TETHYS_DB_PORT} -O ${TETHYS_DB_SUPER_USERNAME} ${TETHYS_DB_SUPER_USERNAME} -E utf-8 -T template0
    fi

    if [ -n "${INITIALIZE_DB}" ]
    then
        # Initialize Tethys database
        tethys manage syncdb
        echo "from django.contrib.auth.models import User; User.objects.create_superuser('${TETHYS_SUPER_USER}', '${TETHYS_SUPER_USER_EMAIL}', '${TETHYS_SUPER_USER_PASS}')" | python "${TETHYS_HOME}/src/manage.py" shell
        pg_ctl -U postgres -D "${TETHYS_DB_DIR}/data" stop
    fi

    echo "Deactivating the ${CONDA_ENV_NAME} environment..."
    conda deactivate

    if [ -n "${CREATE_ENV_SCRIPTS}" ]
    then
        # Create environment activate/deactivate scripts
        mkdir -p "${ACTIVATE_DIR}" "${DEACTIVATE_DIR}"

        echo "export TETHYS_HOME='${TETHYS_HOME}'" >> "${ACTIVATE_SCRIPT}"
        echo "export TETHYS_PORT='${TETHYS_PORT}'" >> "${ACTIVATE_SCRIPT}"
        echo "export TETHYS_DB_PORT='${TETHYS_DB_PORT}'" >> "${ACTIVATE_SCRIPT}"
        echo "export TETHYS_DB_DIR='${TETHYS_DB_DIR}'" >> "${ACTIVATE_SCRIPT}"
        echo "export CONDA_HOME='${CONDA_HOME}'" >> "${ACTIVATE_SCRIPT}"
        echo "export CONDA_ENV_NAME='${CONDA_ENV_NAME}'" >> "${ACTIVATE_SCRIPT}"
        echo "alias tethys_start_db='pg_ctl -U postgres -D \"\${TETHYS_DB_DIR}/data\" -l \"\${TETHYS_DB_DIR}/logfile\" start -o \"-p \${TETHYS_DB_PORT}\"'" >> "${ACTIVATE_SCRIPT}"
        echo "alias tstartdb=tethys_start_db" >> "${ACTIVATE_SCRIPT}"
        echo "alias tethys_stop_db='pg_ctl -U postgres -D \"\${TETHYS_DB_DIR}/data\" stop'" >> "${ACTIVATE_SCRIPT}"
        echo "alias tstopdb=tethys_stop_db" >> "${ACTIVATE_SCRIPT}"
        echo "alias tms='tethys manage start -p ${ALLOWED_HOST}:\${TETHYS_PORT}'" >> "${ACTIVATE_SCRIPT}"
        echo "alias tstart='tstartdb; tms'" >> "${ACTIVATE_SCRIPT}"

        echo "unset TETHYS_HOME" >> "${DEACTIVATE_SCRIPT}"
        echo "unset TETHYS_PORT" >> "${DEACTIVATE_SCRIPT}"
        echo "unset TETHYS_DB_PORT" >> "${DEACTIVATE_SCRIPT}"
        echo "unset TETHYS_DB_DIR" >> "${DEACTIVATE_SCRIPT}"
        echo "unset CONDA_HOME" >> "${DEACTIVATE_SCRIPT}"
        echo "unset CONDA_ENV_NAME" >> "${DEACTIVATE_SCRIPT}"
        echo "unalias tethys_start_db" >> "${DEACTIVATE_SCRIPT}"
        echo "unalias tstartdb" >> "${DEACTIVATE_SCRIPT}"
        echo "unalias tethys_stop_db" >> "${DEACTIVATE_SCRIPT}"
        echo "unalias tstopdb" >> "${DEACTIVATE_SCRIPT}"
        echo "unalias tms" >> "${DEACTIVATE_SCRIPT}"
        echo "unalias tstart" >> "${DEACTIVATE_SCRIPT}"
    fi

    if [ -n "${CREATE_SHORTCUTS}" ]
    then
        echo "# Tethys Platform" >> ~/${BASH_PROFILE}
        echo "alias t='. ${CONDA_HOME}/bin/activate ${CONDA_ENV_NAME}'" >> ~/${BASH_PROFILE}
    fi
fi

# Install Docker (if flag is set)
set +e  # don't exit on error anymore

# Rename some variables for reference after deactivating tethys environment.
TETHYS_CONDA_HOME=${CONDA_HOME}
TETHYS_CONDA_ENV_NAME=${CONDA_ENV_NAME}

#  Install Production configuration if flag is set

ubuntu_debian_production_install() {
    sudo apt update
    sudo apt install -y nginx
    sudo rm /etc/nginx/sites-enabled/default
    NGINX_SITES_DIR='sites-enabled'
}

enterprise_linux_production_install() {
    sudo yum install nginx -y
    sudo systemctl enable nginx
    sudo systemctl start nginx
    sudo firewall-cmd --permanent --zone=public --add-service=http
#    sudo firewall-cmd --permanent --zone=public --add-service=https
    sudo firewall-cmd --reload

    NGINX_SITES_DIR='conf.d'
}

redhat_production_install() {
    VERSION=$(python -c "import platform; print(platform.platform().split('-')[-2][0])")
    sudo bash -c "echo $'[nginx]\nname=nginx repo\nbaseurl=http://nginx.org/packages/rhel/${VERSION}/\$basearch/\ngpgcheck=0\nenabled=1' > /etc/yum.repos.d/nginx.repo"
    enterprise_linux_production_install
}

centos_production_install() {
    PLATFORM=${LINUX_DISTRIBUTION}
    VERSION=$(python -c "import platform; print(platform.platform().split('-')[-2][0])")
    sudo bash -c "echo $'[nginx]\nname=nginx repo\nbaseurl=http://nginx.org/packages/${PLATFORM}/${VERSION}/\$basearch/\ngpgcheck=0\nenabled=1' > /etc/yum.repos.d/nginx.repo"
    sudo yum install epel-release -y
    enterprise_linux_production_install
}

configure_selinux() {
    sudo yum install setroubleshoot -y
    sudo semanage fcontext -a -t httpd_config_t ${TETHYS_HOME}/src/tethys_portal/tethys_nginx.conf
    sudo restorecon -v ${TETHYS_HOME}/src/tethys_portal/tethys_nginx.conf
    sudo semanage fcontext -a -t httpd_sys_content_t "${TETHYS_HOME}(/.*)?"
    sudo semanage fcontext -a -t httpd_sys_content_t "${TETHYS_HOME}/static(/.*)?"
    sudo semanage fcontext -a -t httpd_sys_rw_content_t "${TETHYS_HOME}/workspaces(/.*)?"
    sudo restorecon -R -v ${TETHYS_HOME} > /dev/null
    echo $'module tethys-selinux-policy 1.0;\nrequire {type httpd_t; type init_t; class unix_stream_socket connectto; }\n#============= httpd_t ==============\nallow httpd_t init_t:unix_stream_socket connectto;' > ${TETHYS_HOME}/src/tethys_portal/tethys-selinux-policy.te

    checkmodule -M -m -o ${TETHYS_HOME}/src/tethys_portal/tethys-selinux-policy.mod ${TETHYS_HOME}/src/tethys_portal/tethys-selinux-policy.te
    semodule_package -o ${TETHYS_HOME}/src/tethys_portal/tethys-selinux-policy.pp -m ${TETHYS_HOME}/src/tethys_portal/tethys-selinux-policy.mod
    sudo semodule -i ${TETHYS_HOME}/src/tethys_portal/tethys-selinux-policy.pp
}

if [ -n "${LINUX_DISTRIBUTION}" -a "${PRODUCTION}" = "true" ]
then
    # prompt for sudo
    echo "Production installation requires some commands to be run with sudo. Please enter password:"
    sudo echo "Installing Tethys Production Server..."

    case ${LINUX_DISTRIBUTION} in
        debian)
            ubuntu_debian_production_install
        ;;
        ubuntu)
            ubuntu_debian_production_install
        ;;
        centos)
            centos_production_install
        ;;
        redhat)
            redhat_production_install
        ;;
        fedora)
            enterprise_linux_production_install
        ;;
        *)
            echo "Automated production installation on ${LINUX_DISTRIBUTION} is not supported."
        ;;
    esac

    source "${CONDA_HOME}/etc/profile.d/conda.sh"
    conda activate ${CONDA_ENV_NAME}
    pg_ctl -U postgres -D "${TETHYS_DB_DIR}/data" -l "${TETHYS_DB_DIR}/logfile" start -o "-p ${TETHYS_DB_PORT}"
    echo "Waiting for databases to startup..."; sleep 5
    conda install -c conda-forge uwsgi -y
    tethys gen settings --production --allowed-host=${ALLOWED_HOST} --db-username ${TETHYS_DB_USERNAME} --db-password ${TETHYS_DB_PASSWORD} --db-port ${TETHYS_DB_PORT} --overwrite
    tethys gen nginx --overwrite
    tethys gen uwsgi_settings --overwrite
    tethys gen uwsgi_service --overwrite
    NGINX_USER=$(grep 'user .*;' /etc/nginx/nginx.conf | awk '{print $2}' | awk -F';' '{print $1}')
    NGINX_GROUP=${NGINX_USER}
    NGINX_HOME=$(grep ${NGINX_USER} /etc/passwd | awk -F':' '{print $6}')
    mkdir -p ${TETHYS_HOME}/static ${TETHYS_HOME}/workspaces ${TETHYS_HOME}/apps
    sudo chown -R ${USER} ${TETHYS_HOME}
    tethys manage collectall --noinput
    sudo chmod 705 ~
    sudo mkdir /var/log/uwsgi
    sudo touch /var/log/uwsgi/tethys.log
    sudo ln -s ${TETHYS_HOME}/src/tethys_portal/tethys_nginx.conf /etc/nginx/${NGINX_SITES_DIR}/

    if [ -n "${SELINUX}" ]
    then
        configure_selinux
    fi

    sudo chown -R ${NGINX_USER}:${NGINX_GROUP} ${TETHYS_HOME}/src /var/log/uwsgi/tethys.log
    sudo systemctl enable ${TETHYS_HOME}/src/tethys_portal/tethys.uwsgi.service
    sudo systemctl start tethys.uwsgi.service
    sudo systemctl restart nginx
    set +x
    conda deactivate

    echo "export NGINX_USER='${NGINX_USER}'" >> "${ACTIVATE_SCRIPT}"
    echo "export NGINX_HOME='${NGINX_HOME}'" >> "${ACTIVATE_SCRIPT}"
    echo "alias tethys_user_own='sudo chown -R \${USER} \"\${TETHYS_HOME}/src\" \"\${TETHYS_HOME}/static\" \"\${TETHYS_HOME}/workspaces\" \"\${TETHYS_HOME}/apps\"'" >> "${ACTIVATE_SCRIPT}"
    echo "alias tuo=tethys_user_own" >> "${ACTIVATE_SCRIPT}"
    echo "alias tethys_server_own='sudo chown -R \${NGINX_USER}:\${NGINX_USER} \"\${TETHYS_HOME}/src\" \"\${TETHYS_HOME}/static\" \"\${TETHYS_HOME}/workspaces\" \"\${TETHYS_HOME}/apps\"'" >> "${ACTIVATE_SCRIPT}"
    echo "alias tso=tethys_server_own" >> "${ACTIVATE_SCRIPT}"
    echo "alias tethys_server_restart='tso; sudo systemctl restart tethys.uwsgi.service; sudo systemctl restart nginx'" >> "${ACTIVATE_SCRIPT}"
    echo "alias tsr=tethys_server_restart" >> "${ACTIVATE_SCRIPT}"

    echo "unset NGINX_USER" >> "${DEACTIVATE_SCRIPT}"
    echo "unset NGINX_HOME" >> "${DEACTIVATE_SCRIPT}"
    echo "unalias tethys_user_own" >> "${DEACTIVATE_SCRIPT}"
    echo "unalias tuo" >> "${DEACTIVATE_SCRIPT}"
    echo "unalias tethys_server_own" >> "${DEACTIVATE_SCRIPT}"
    echo "unalias tso" >> "${DEACTIVATE_SCRIPT}"
    echo "unalias tethys_server_restart" >> "${DEACTIVATE_SCRIPT}"
    echo "unalias trs" >> "${DEACTIVATE_SCRIPT}"
fi


# Install Docker (if flag is set

installation_warning(){
    echo "WARNING: installing docker on $1 is not officially supported by the Tethys install script. Attempting to install with $2 script."
}

finalize_docker_install(){
    sudo groupadd docker
    sudo gpasswd -a ${USER} docker
    source "${CONDA_HOME}/etc/profile.d/conda.sh"
    conda activate ${CONDA_ENV_NAME}
    sg docker -c "tethys docker init ${DOCKER_OPTIONS}"
    conda deactivate
    echo "Docker installation finished!"
    echo "You must re-login for Docker permissions to be activated."
    echo "(Alternatively you can run 'newgrp docker')"
}

ubuntu_debian_docker_install(){
    if [ "${LINUX_DISTRIBUTION}" != "ubuntu" ] && [ ${LINUX_DISTRIBUTION} != "debian" ]
    then
        installation_warning ${LINUX_DISTRIBUTION} "Ubuntu"
    fi

    sudo apt-get update
    sudo apt-get install -y apt-transport-https ca-certificates curl gnupg2 software-properties-common
    curl -fsSL https://download.docker.com/linux/${LINUX_DISTRIBUTION}/gpg | sudo apt-key add -
    sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/${LINUX_DISTRIBUTION} $(lsb_release -cs) stable"
    sudo apt-get update
    sudo apt-get install -y docker-ce

    finalize_docker_install
}

centos_docker_install(){
    if [ "${LINUX_DISTRIBUTION}" != "centos" ]
    then
        installation_warning ${LINUX_DISTRIBUTION} "CentOS"
    fi

    sudo yum -y install yum-utils
    sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
    sudo yum makecache fast
    sudo yum -y install docker-ce
    sudo systemctl start docker
    sudo systemctl enable docker

    finalize_docker_install
}

fedora_docker_install(){
    if [ "${LINUX_DISTRIBUTION}" != "fedora" ]
    then
        installation_warning ${LINUX_DISTRIBUTION} "Fedora"
    fi

    sudo dnf -y install -y dnf-plugins-core
    sudo dnf config-manager --add-repo https://download.docker.com/linux/fedora/docker-ce.repo
    sudo dnf makecache fast
    sudo dnf -y install docker-ce
    sudo systemctl start docker
    sudo systemctl enable docker

    finalize_docker_install
}

if [ -n "${LINUX_DISTRIBUTION}" -a "${INSTALL_DOCKER}" = "true" ]
then
    # prompt for sudo
    echo "Docker installation requires some commands to be run with sudo. Please enter password:"
    sudo echo "Installing Docker..."

    case ${LINUX_DISTRIBUTION} in
        debian)
            ubuntu_debian_docker_install
        ;;
        ubuntu)
            ubuntu_debian_docker_install
        ;;
        centos)
            centos_docker_install
        ;;
        redhat)
            centos_docker_install
        ;;
        fedora)
            fedora_docker_install
        ;;
        *)
            echo "Automated Docker installation on ${LINUX_DISTRIBUTION} is not supported. Please see https://docs.docker.com/engine/installation/ for more information on installing Docker."
        ;;
    esac
fi


if [ -z "${SKIP_TETHYS_INSTALL}" ]
then
    echo "Tethys installation complete!"
    echo
    if [ -n "${CREATE_SHORTCUTS}" ]
    then
        echo "NOTE: to enable the new alias 't' which activates the tethys environment you must run '. ~/${BASH_PROFILE}'"
    fi
fi

on_exit(){
    set +e
    set +x
}
trap on_exit EXIT
