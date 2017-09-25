#!/bin/bash

USAGE="USAGE: . install_tethys.sh [options]\n
\n
OPTIONS:\n
    -t, --tethys-home <PATH>            Path for tethys home directory. Default is ~/tethys.\n
    -a, --allowed-host <HOST>           Hostname or IP address on which to serve tethys. Default is 127.0.0.1.\n
    -p, --port <PORT>                   Port on which to serve tethys. Default is 8000.\n
    -b, --branch <BRANCH_NAME>          Branch to checkout from version control. Default is 'release'.\n
    -c, --conda-home <PATH>             Path where Miniconda will be installed, or to an existing installation of Miniconda. Default is \${TETHYS_HOME}/miniconda.\n
    -n, --conda-env-name <NAME>         Name for tethys conda environment. Default is 'tethys'.
    --python-version <PYTHON_VERSION>   Main python version to install tethys environment into (2 or 3). Default is 2.\n
    --db-username <USERNAME>            Username that the tethys database server will use. Default is 'tethys_default'.\n
    --db-password <PASSWORD>            Password that the tethys database server will use. Default is 'pass'.\n
    --db-port <PORT>                    Port that the tethys database server will use. Default is 5436.\n
    -S, --superuser <USERNAME>          Tethys super user name. Default is 'admin'.\n
    -E, --superuser-email <EMAIL>       Tethys super user email. Default is ''.\n
    -P, --superuser-pass <PASSWORD>     Tethys super user password. Default is 'pass'.\n
    --skip-tethys-install               Flag to skip the Tethys installation so that the Docker installation or production installation can be added to an existing Tethys installation.\n
    --install-docker                    Flag to include Docker installation as part of the install script (Linux only).\n
    --docker-options <OPTIONS>          Command line options to pass to the 'tethys docker init' call if --install-docker is used. Default is \"'-d'\".\n
    --production                        Flag to install Tethys in a production configuration.\n
    --configure-selinux                 Flag to perform configuration of SELinux for production installation. (Linux only).\n
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
    LINUX_DISTRIBUTION=$(lsb_release -is) || LINUX_DISTRIBUTION=$(python -c "import platform; print(platform.linux_distribution(full_distribution_name=0)[0])")
    # convert to lower case
    echo "Linux Distribution: ${LINUX_DISTRIBUTION}"
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
TETHYS_DB_HOST='127.0.0.1'
TETHYS_DB_PORT=5436
TETHYS_DB_CREATE=0
CONDA_ENV_NAME='tethys'
PYTHON_VERSION='2'
BRANCH='release'

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
    set_option_value TETHYS_DB_PASS "$2"
    shift # past argument
    ;;
    --db-port)
    set_option_value TETHYS_DB_PORT "$2"
    shift # past argument
    ;;
    --db-host)
    set_option_value TETHYS_DB_HOST "$2"
    shift # past argument
    ;;
    --db-create)
    set_option_value TETHYS_DB_CREATE "$2"
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
    echo Ignoring unrecognized option: $key
    ;;
esac
shift # past argument or value
done

# resolve relative paths
resolve_relative_path TETHYS_HOME ${TETHYS_HOME}

# set CONDA_HOME relative to TETHYS_HOME if not already set
if [ -z ${CONDA_HOME} ]
then
    CONDA_HOME="${TETHYS_HOME}/miniconda"
else
    resolve_relative_path CONDA_HOME ${CONDA_HOME}
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
    echo "Starting Tethys Setup..."
    . ${CONDA_HOME}/bin/activate ${CONDA_ENV_NAME}
    tethys gen settings ${ALLOWED_HOST_OPT} --db-username ${TETHYS_DB_USERNAME} --db-password ${TETHYS_DB_PASSWORD} --db-port ${TETHYS_DB_PORT}
    sed -i -e "s/'HOST': '127.0.0.1',/'HOST': '${TETHYSBUILD_DB_HOST}',/g" /usr/lib/tethys/src/tethys_portal/settings.py
    sed -i -e 's/BYPASS_TETHYS_HOME = False/BYPASS_TETHYS_HOME = True/g' /usr/lib/tethys/src/tethys_portal/settings.py
    sed -i -e "s/#TETHYS_WORKSPACES_ROOT = '\/var\/www\/tethys\/static\/workspaces'/TETHYS_WORKSPACES_ROOT = '\/usr\/lib\/tethys\/workspaces'/g" /usr/lib/tethys/src/tethys_portal/settings.py
    # sed -i -e "s/127.0.0.1/${TETHYS_DB_HOST}/g" /usr/lib/tethys/src/tethys_portal/settings.py
    # Setup local database
    echo "Setting up the Tethys database..."
    # initdb  -U postgres -D "${TETHYS_HOME}/psql/data"
    # pg_ctl -U postgres -D "${TETHYS_HOME}/psql/data" -l "${TETHYS_HOME}/psql/logfile" start -o "-p ${TETHYS_DB_PORT}"
    echo "Waiting for databases to startup..."; sleep 30
    if [[ $(psql -U postgres -h ${TETHYS_DB_HOST} -p ${TETHYS_DB_PORT} --command "SELECT 1 FROM pg_roles WHERE rolname='${TETHYS_DB_USERNAME}'" | grep -q 1 && echo $?) -ne 0 ]]; then 
    # if [[ "${TETHYS_DB_CREATE}" -ne '0' ]]; then
      echo "Creating DB User and Password"
      psql -U postgres -h ${TETHYS_DB_HOST} -p ${TETHYS_DB_PORT} --command "CREATE USER ${TETHYS_DB_USERNAME} WITH NOCREATEDB NOCREATEROLE NOSUPERUSER PASSWORD '${TETHYS_DB_PASSWORD}';"
      createdb -U postgres -h ${TETHYS_DB_HOST} -p ${TETHYS_DB_PORT} -O ${TETHYS_DB_USERNAME} ${TETHYS_DB_USERNAME} -E utf-8 -T template0
    fi

    # Initialze Tethys database
    cd /usr/lib/tethys/src
    tethys manage syncdb
    if [[ $(psql -U postgres -h ${TETHYS_DB_HOST} -p ${TETHYS_DB_PORT} --command "SELECT 1 FROM pg_roles WHERE rolname='${TETHYS_DB_USERNAME}'" | grep -q 1 && echo $?) -ne 0 ]]; then 
    # if [[ "${TETHYS_DB_CREATE}" -ne '0' ]]; then
      echo "from django.contrib.auth.models import User; User.objects.create_superuser('${TETHYS_SUPER_USER}', '${TETHYS_SUPER_USER_EMAIL}', '${TETHYS_SUPER_USER_PASS}')" | python manage.py shell
    fi
    # pg_ctl -U postgres -D "${TETHYS_HOME}/psql/data" stop
    . deactivate


    # Create environment activate/deactivate scripts
    mkdir -p "${ACTIVATE_DIR}" "${DEACTIVATE_DIR}"

    echo "export TETHYS_HOME='${TETHYS_HOME}'" >> "${ACTIVATE_SCRIPT}"
    echo "export TETHYS_PORT='${TETHYS_PORT}'" >> "${ACTIVATE_SCRIPT}"
    echo "export TETHYS_DB_PORT='${TETHYS_DB_PORT}'" >> "${ACTIVATE_SCRIPT}"
    echo "export CONDA_HOME='${CONDA_HOME}'" >> "${ACTIVATE_SCRIPT}"
    echo "export CONDA_ENV_NAME='${CONDA_ENV_NAME}'" >> "${ACTIVATE_SCRIPT}"
    echo "alias tethys_start_db='pg_ctl -U postgres -D \"\${TETHYS_HOME}/psql/data\" -l \"\${TETHYS_HOME}/psql/logfile\" start -o \"-p \${TETHYS_DB_PORT}\"'" >> "${ACTIVATE_SCRIPT}"
    echo "alias tstartdb=tethys_start_db" >> "${ACTIVATE_SCRIPT}"
    echo "alias tethys_stop_db='pg_ctl -U postgres -D \"\${TETHYS_HOME}/psql/data\" stop'" >> "${ACTIVATE_SCRIPT}"
    echo "alias tstopdb=tethys_stop_db" >> "${ACTIVATE_SCRIPT}"
    echo "alias tms='tethys manage start -p ${ALLOWED_HOST}:\${TETHYS_PORT}'" >> "${ACTIVATE_SCRIPT}"
    echo "alias tstart='tstartdb; tms'" >> "${ACTIVATE_SCRIPT}"

    echo "unset TETHYS_HOME" >> "${DEACTIVATE_SCRIPT}"
    echo "unset TETHYS_PORT" >> "${DEACTIVATE_SCRIPT}"
    echo "unset TETHYS_DB_PORT" >> "${DEACTIVATE_SCRIPT}"
    echo "unset CONDA_HOME" >> "${DEACTIVATE_SCRIPT}"
    echo "unset CONDA_ENV_NAME" >> "${DEACTIVATE_SCRIPT}"
    echo "unalias tethys_start_db" >> "${DEACTIVATE_SCRIPT}"
    echo "unalias tstartdb" >> "${DEACTIVATE_SCRIPT}"
    echo "unalias tethys_stop_db" >> "${DEACTIVATE_SCRIPT}"
    echo "unalias tstopdb" >> "${DEACTIVATE_SCRIPT}"
    echo "unalias tms" >> "${DEACTIVATE_SCRIPT}"
    echo "unalias tstart" >> "${DEACTIVATE_SCRIPT}"

    echo "# Tethys Platform" >> ~/${BASH_PROFILE}
    echo "alias t='. ${CONDA_HOME}/bin/activate ${CONDA_ENV_NAME}'" >> ~/${BASH_PROFILE}
fi

# Install Docker (if flag is set)
set +e  # don't exit on error anymore

# Rename some variables for reference after deactivating tethys environment.
TETHYS_CONDA_HOME=${CONDA_HOME}
TETHYS_CONDA_ENV_NAME=${CONDA_ENV_NAME}

#  Install Production configuration if flag is set

ubuntu_debian_production_install() {
    apt update
    apt install -y nginx
    rm /etc/nginx/sites-enabled/default
    NGINX_SITES_DIR='sites-enabled'
}

enterprise_linux_production_install() {
    yum install nginx -y
    systemctl enable nginx
    systemctl start nginx
    firewall-cmd --permanent --zone=public --add-service=http
#    firewall-cmd --permanent --zone=public --add-service=https
    firewall-cmd --reload

    NGINX_SITES_DIR='conf.d'
}

redhat_production_install() {
    VERSION=$(python -c "import platform; print(platform.platform().split('-')[-2][0])")
    bash -c "echo $'[nginx]\nname=nginx repo\nbaseurl=http://nginx.org/packages/rhel/${VERSION}/\$basearch/\ngpgcheck=0\nenabled=1' > /etc/yum.repos.d/nginx.repo"
    enterprise_linux_production_install
}

centos_production_install() {
    PLATFORM=${LINUX_DISTRIBUTION}
    VERSION=$(python -c "import platform; print(platform.platform().split('-')[-2][0])")
    bash -c "echo $'[nginx]\nname=nginx repo\nbaseurl=http://nginx.org/packages/${PLATFORM}/${VERSION}/\$basearch/\ngpgcheck=0\nenabled=1' > /etc/yum.repos.d/nginx.repo"
    yum install epel-release -y
    enterprise_linux_production_install
}

configure_selinux() {
    yum install setroubleshoot -y
    semanage fcontext -a -t httpd_config_t ${TETHYS_HOME}/src/tethys_portal/tethys_nginx.conf
    restorecon -v ${TETHYS_HOME}/src/tethys_portal/tethys_nginx.conf
    semanage fcontext -a -t httpd_sys_content_t "${TETHYS_HOME}(/.*)?"
    semanage fcontext -a -t httpd_sys_content_t "${TETHYS_HOME}/static(/.*)?"
    semanage fcontext -a -t httpd_sys_rw_content_t "${TETHYS_HOME}/workspaces(/.*)?"
    restorecon -R -v ${TETHYS_HOME} > /dev/null
    echo $'module tethys-selinux-policy 1.0;\nrequire {type httpd_t; type init_t; class unix_stream_socket connectto; }\n#============= httpd_t ==============\nallow httpd_t init_t:unix_stream_socket connectto;' > ${TETHYS_HOME}/src/tethys_portal/tethys-selinux-policy.te

    checkmodule -M -m -o ${TETHYS_HOME}/src/tethys_portal/tethys-selinux-policy.mod ${TETHYS_HOME}/src/tethys_portal/tethys-selinux-policy.te
    semodule_package -o ${TETHYS_HOME}/src/tethys_portal/tethys-selinux-policy.pp -m ${TETHYS_HOME}/src/tethys_portal/tethys-selinux-policy.mod
    semodule -i ${TETHYS_HOME}/src/tethys_portal/tethys-selinux-policy.pp
}

if [ -n "${LINUX_DISTRIBUTION}" -a "${PRODUCTION}" = "true" ]
then
    # prompt for sudo
    echo "Installing Tethys Production Server..."

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


    . ${CONDA_HOME}/bin/activate ${CONDA_ENV_NAME}
    pg_ctl -U postgres -D "${TETHYS_HOME}/psql/data" -l "${TETHYS_HOME}/psql/logfile" start -o "-p ${TETHYS_DB_PORT}"
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
    chown -R ${USER} ${TETHYS_HOME}
    tethys manage collectall --noinput
    chmod 705 ~
    mkdir /var/log/uwsgi
    touch /var/log/uwsgi/tethys.log
    ln -s ${TETHYS_HOME}/src/tethys_portal/tethys_nginx.conf /etc/nginx/${NGINX_SITES_DIR}/

    if [ -n "${SELINUX}" ]
    then
        configure_selinux
    fi

    chown -R ${NGINX_USER}:${NGINX_GROUP} ${TETHYS_HOME}/src /var/log/uwsgi/tethys.log
    systemctl enable ${TETHYS_HOME}/src/tethys_portal/tethys.uwsgi.service
    systemctl start tethys.uwsgi.service
    systemctl restart nginx
    set +x
    . deactivate

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


if [ -z "${SKIP_TETHYS_INSTALL}" ]
then
    echo "Tethys installation complete!"
    echo
    echo "NOTE: to enable the new alias 't' which activates the tethys environment you must run '. ~/${BASH_PROFILE}'"
fi

on_exit(){
    set +e
    set +x
}
trap on_exit EXIT

