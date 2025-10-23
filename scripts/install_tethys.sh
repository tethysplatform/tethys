#!/bin/bash

RED=`tput setaf 1`
GREEN=`tput setaf 2`
YELLOW=`tput setaf 3`
RESET_COLOR=`tput sgr0`

USAGE="USAGE: . install_tethys.sh [options]\n
\n
OPTIONS:\n
\t    -n, --conda-env-name <NAME>         \t\t Name for tethys conda environment. Default is 'tethys-dev'.\n
\t    -t, --tethys-home <PATH>            \t\t Path for tethys home directory. Default is ~/.tethys/${CONDA_ENV_NAME}.\n
\t    -s, --tethys-src <PATH>             \t\t Path for tethys source directory. Default is \${TETHYS_HOME}/tethys.\n
\t    -a, --allowed-hosts <HOST>          \t\t Hostname or IP address on which to serve tethys. Default is 127.0.0.1.\n
\t    -p, --port <PORT>                   \t\t\t Port on which to serve tethys. Default is 8000.\n
\t    -b, --branch <BRANCH_NAME>          \t\t Branch to checkout from version control. Default is 'main'.\n
\t    -c, --conda-home <PATH>             \t\t Path where Miniconda will be installed, or to an existing installation of Miniconda. Default is ~/miniconda.\n
\t    -d, --django-version <VERSION>      \t\t Version of Django to install. Default is '4.2'.\n
\t    --python-version <VERSION>      \t\t Version of Python to install. Default is '3.12'.\n
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
\t        \t\t c - Checkout the branch specified by the option '--branch' (specifying the flag 'r' will also trigger this flag)\n
\t        \t\t e - Create Conda environment\n
\t        \t\t s - Create 'portal_config.yml' file and configure settings\n
\t        \t\t d - Create a local database server\n
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

resolve_relative_path ()
{
    local __path_var="$1"
    eval $__path_var="'$($(which python || which python3) -c "import os; print(os.path.abspath('$2'))")'"
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
elif [ "$(uname)" = "Darwin" ]  # i.e. MacOSX
then
    MINICONDA_URL="https://repo.continuum.io/miniconda/Miniconda3-latest-MacOSX-x86_64.sh"
    BASH_PROFILE=".bash_profile"
else
    echo $(uname) is not a supported operating system.
    exit
fi

# Set default options
ALLOWED_HOST='127.0.0.1'
TETHYS_PORT=8000
TETHYS_DB_USERNAME='tethys_default'
TETHYS_DB_PASSWORD='pass'
TETHYS_DB_SUPER_USERNAME='tethys_super'
TETHYS_DB_SUPER_PASSWORD='pass'
TETHYS_DB_PORT=5436
TETHYS_DB_DIR='psql'
CONDA_HOME=~/miniconda
PYTHON_VERSION='3.12'
DJANGO_VERSION='4.2'
CONDA_ENV_NAME='tethys-dev'
BRANCH='main'

TETHYS_SUPER_USER='admin'
TETHYS_SUPER_USER_EMAIL=''
TETHYS_SUPER_USER_PASS='pass'

DOCKER_OPTIONS='-d'

INSTALL_MINICONDA="true"
CLONE_REPO="true"
CHECKOUT_BRANCH="true"
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
    -s|--tethys-src)
    set_option_value TETHYS_SRC "$2"
    shift # past argument
    ;;
    -a|--allowed-hosts)
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
    -d|--django-version)
    set_option_value DJANGO_VERSION "$2"
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
        CHECKOUT_BRANCH=
        CREATE_ENV=
        CREATE_SETTINGS=
        SETUP_DB=
        CREATE_ENV_SCRIPTS=
        CREATE_SHORTCUTS=

        if [[ "$2" = *"m"* ]]; then
            INSTALL_MINICONDA="true"
        fi
        if [[ "$2" = *"r"* ]]; then
            CLONE_REPO="true"
        fi
        if [[ "$2" = *"c"* ]]; then
            CHECKOUT_BRANCH="true"
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
        echo SELinux configuration is not supported on $(uname). Ignoring option $key.
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

if [ -z "${TETHYS_HOME}" ]
then
  TETHYS_HOME=~/.tethys
  if [ "${CONDA_ENV_NAME}" != "tethys" ]
  then
    TETHYS_HOME=${TETHYS_HOME}/${CONDA_ENV_NAME}
  fi
fi

# resolve relative paths
resolve_relative_path TETHYS_HOME ${TETHYS_HOME}
export TETHYS_HOME=${TETHYS_HOME}

resolve_relative_path CONDA_HOME ${CONDA_HOME}

# set TETHYS_SRC relative to TETHYS_HOME if not already set
if [ -z "${TETHYS_SRC}" ]
then
    TETHYS_SRC="${TETHYS_HOME}/tethys"
else
    resolve_relative_path TETHYS_SRC ${TETHYS_SRC}
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

    # Install mamba
    echo "Installing mamba..."
    conda update -n base conda
    conda install -n base conda-libmamba-solver
    conda config --set solver libmamba

    if [ -n "${CLONE_REPO}" ]
    then
        # clone Tethys repo
        echo "Cloning the Tethys Platform repo..."
        conda activate
        conda install --yes git
        git clone https://github.com/tethysplatform/tethys.git "${TETHYS_SRC}"
    fi

    if [ -n "${CHECKOUT_BRANCH}" ] || [ -n "${CLONE_REPO}" ]
    then
        cd "${TETHYS_SRC}"
        conda activate
        git checkout ${BRANCH}
    fi

    if [ -n "${CREATE_ENV}" ]
    then
        # create conda env and install Tethys
        echo "Setting up the ${CONDA_ENV_NAME} environment..."
        sudo sed "s/python>=.*/python=${PYTHON_VERSION}/" "${TETHYS_SRC}/environment.yml" > "${TETHYS_SRC}/generated_environment.yml"
        sudo sed -i.bak "s/django>=.*/django=${DJANGO_VERSION}/" "${TETHYS_SRC}/generated_environment.yml"
        conda env create -n ${CONDA_ENV_NAME} -f "${TETHYS_SRC}/generated_environment.yml"
        conda activate ${CONDA_ENV_NAME}
        pip install --no-deps -e ${TETHYS_SRC}
    else
        echo "Activating the ${CONDA_ENV_NAME} environment..."
        conda activate ${CONDA_ENV_NAME}
    fi

    if [ -n "${CREATE_SETTINGS}" ]
    then
        tethys gen portal_config
        tethys settings \
          --set ALLOWED_HOSTS "[${ALLOWED_HOST}]" \
          --set DATABASES.default.USER ${TETHYS_DB_SUPER_USERNAME} \
          --set DATABASES.default.PASSWORD ${TETHYS_DB_PASSWORD} \
          --set DATABASES.default.PORT ${TETHYS_DB_PORT} \
          --set DATABASES.default.DIR ${TETHYS_DB_DIR} \
          --set DATABASES.default.ENGINE django.db.backends.postgresql
        cat ${TETHYS_HOME}/portal_config.yml
    fi

    if [ -n "${SETUP_DB}" ]
    then
        # Setup local database
        echo "Setting up the Tethys database..."
        tethys db configure --username ${TETHYS_DB_USERNAME} --password ${TETHYS_DB_PASSWORD} --superuser-name ${TETHYS_DB_SUPER_USERNAME} --superuser-password ${TETHYS_DB_SUPER_PASSWORD} --portal-superuser-name ${TETHYS_SUPER_USER} --portal-superuser-email '${TETHYS_SUPER_USER_EMAIL}' --portal-superuser-pass ${TETHYS_SUPER_USER_PASS}
        tethys db stop
    fi

    if [ -n "${CREATE_ENV_SCRIPTS}" ]
    then
        # Create environment activatescripts
        mkdir -p "${ACTIVATE_DIR}"

        echo "alias tms='tethys manage start -p ${ALLOWED_HOST}:${TETHYS_PORT}'" >> "${ACTIVATE_SCRIPT}"
        echo "alias tstart='tethys db start; tms'" >> "${ACTIVATE_SCRIPT}"
    fi

    if [ -n "${CREATE_SHORTCUTS}" ]
    then
        echo "# Tethys Platform" >> ~/${BASH_PROFILE}
        echo "alias t='source ${CONDA_HOME}/etc/profile.d/conda.sh; conda activate ${CONDA_ENV_NAME}'" >> ~/${BASH_PROFILE}
    fi

    echo "Deactivating the ${CONDA_ENV_NAME} environment..."
    conda deactivate

        if [ -n "${CREATE_ENV_SCRIPTS}" ]
    then
        # Create environment deactivate scripts
        mkdir -p "${DEACTIVATE_DIR}"

        echo "unalias tms" >> "${DEACTIVATE_SCRIPT}"
        echo "unalias tstart" >> "${DEACTIVATE_SCRIPT}"
    fi
fi

# Install Docker (if flag is set)
set +e  # don't exit on error anymore

#  Install Production configuration if flag is set

ubuntu_debian_production_install() {
    sudo apt update
    sudo apt install -y nginx supervisor
    sudo rm /etc/nginx/sites-enabled/default
    NGINX_SITES_DIR='sites-enabled'
    SUPERVISOR_SITES_DIR='supervisor/conf.d'
}

enterprise_linux_production_install() {
    sudo yum install supervisor nginx -y
    sudo systemctl enable supervisord
    sudo systemctl start supervisord
    sudo firewall-cmd --permanent --zone=public --add-service=http
    sudo firewall-cmd --reload

    NGINX_SITES_DIR='conf.d'
    sudo sed -i '$ s@$@ /etc/supervisord.d/*.conf@' "/etc/supervisord.conf"
    SUPERVISOR_SITES_DIR='supervisord.d'
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
    sudo semanage fcontext -a -t httpd_config_t ${TETHYS_HOME}/tethys_nginx.conf
    sudo restorecon -v ${TETHYS_HOME}/tethys_nginx.conf
    sudo semanage fcontext -a -t httpd_sys_content_t "${TETHYS_HOME}(/.*)?"
    sudo semanage fcontext -a -t httpd_sys_content_t "${TETHYS_HOME}/static(/.*)?"
    sudo semanage fcontext -a -t httpd_sys_rw_content_t "${TETHYS_HOME}/workspaces(/.*)?"
    sudo restorecon -R -v ${TETHYS_HOME} > /dev/null
    echo $'module tethys-selinux-policy 1.0;\nrequire {type httpd_t; type init_t; class unix_stream_socket connectto; }\n#============= httpd_t ==============\nallow httpd_t init_t:unix_stream_socket connectto;' > ${TETHYS_HOME}/tethys-selinux-policy.te

    checkmodule -M -m -o ${TETHYS_HOME}/tethys-selinux-policy.mod ${TETHYS_HOME}/tethys-selinux-policy.te
    semodule_package -o ${TETHYS_HOME}/tethys-selinux-policy.pp -m ${TETHYS_HOME}/tethys-selinux-policy.mod
    sudo semodule -i ${TETHYS_HOME}/tethys-selinux-policy.pp
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
    tethys db start
    tethys settings --set DEBUG False
    tethys gen nginx --overwrite
    tethys gen nginx_service --overwrite
    tethys gen asgi_service --overwrite
    NGINX_USER=$(grep 'user .*;' /etc/nginx/nginx.conf | awk '{print $2}' | awk -F';' '{print $1}')
    NGINX_GROUP=${NGINX_USER}
    NGINX_HOME=$(grep ${NGINX_USER} /etc/passwd | awk -F':' '{print $6}')
    mkdir -p ${TETHYS_HOME}/static ${TETHYS_HOME}/workspaces ${TETHYS_HOME}/apps
    sudo chown -R ${USER} ${TETHYS_HOME}
    tethys manage collectall --noinput
    sudo chmod 705 ~
    sudo mkdir /var/log/tethys
    sudo touch /var/log/tethys/tethys.log
    sudo ln -s ${TETHYS_HOME}/tethys_nginx.conf /etc/nginx/${NGINX_SITES_DIR}/

    if [ -n "${SELINUX}" ]
    then
        configure_selinux
    fi

    sudo chown -R ${NGINX_USER}:${NGINX_GROUP} ${TETHYS_SRC} /var/log/tethys/tethys.log
    sudo mkdir -p /run/asgi; sudo chown ${NGINX_USER}:${NGINX_USER} /run/asgi
    sudo ln -s ${TETHYS_HOME}/asgi_supervisord.conf /etc/${SUPERVISOR_SITES_DIR}/asgi_supervisord.conf
    sudo ln -s ${TETHYS_HOME}/nginx_supervisord.conf /etc/${SUPERVISOR_SITES_DIR}/nginx_supervisord.conf
    sudo supervisorctl reread
    sudo supervisorctl update
    set +x
    conda deactivate

    echo "export NGINX_USER='${NGINX_USER}'" >> "${ACTIVATE_SCRIPT}"
    echo "export NGINX_HOME='${NGINX_HOME}'" >> "${ACTIVATE_SCRIPT}"
    echo "alias tethys_user_own='sudo chown -R \${USER} \"${TETHYS_SRC}\" \"${TETHYS_HOME}/static\" \"${TETHYS_HOME}/workspaces\" \"${TETHYS_HOME}/apps\"'" >> "${ACTIVATE_SCRIPT}"
    echo "alias tuo=tethys_user_own" >> "${ACTIVATE_SCRIPT}"
    echo "alias tethys_server_own='sudo chown -R \${NGINX_USER}:\${NGINX_USER} \"${TETHYS_SRC}\" \"${TETHYS_HOME}/static\" \"${TETHYS_HOME}/workspaces\" \"${TETHYS_HOME}/apps\"'" >> "${ACTIVATE_SCRIPT}"
    echo "alias tso=tethys_server_own" >> "${ACTIVATE_SCRIPT}"
    echo "alias tethys_server_restart='tso; sudo supervisorctl restart all;'" >> "${ACTIVATE_SCRIPT}"
    echo "alias tsr=tethys_server_restart" >> "${ACTIVATE_SCRIPT}"

    echo "unset NGINX_USER" >> "${DEACTIVATE_SCRIPT}"
    echo "unset NGINX_HOME" >> "${DEACTIVATE_SCRIPT}"
    echo "unalias tethys_user_own" >> "${DEACTIVATE_SCRIPT}"
    echo "unalias tuo" >> "${DEACTIVATE_SCRIPT}"
    echo "unalias tethys_server_own" >> "${DEACTIVATE_SCRIPT}"
    echo "unalias tso" >> "${DEACTIVATE_SCRIPT}"
    echo "unalias tethys_server_restart" >> "${DEACTIVATE_SCRIPT}"
    echo "unalias tsr" >> "${DEACTIVATE_SCRIPT}"
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
