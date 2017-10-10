#!/bin/bash

USAGE="USAGE: . install_tethys.sh [options]\n
\n
OPTIONS:\n
    -t, --tethys-home <PATH>            Path for tethys home directory. Default is ~/tethys.\n
    -a, --allowed-host <HOST>           Hostname or IP address on which to serve tethys. Default is 127.0.0.1.\n
    -p, --port <PORT>                   Port on which to serve tethys. Default is 8000.\n
    --python-version <PYTHON_VERSION>   Main python version to install tethys environment into (2 or 3). Default is 2.\n
    --db-username <USERNAME>            Username that the tethys database server will use. Default is 'tethys_default'.\n
    --db-password <PASSWORD>            Password that the tethys database server will use. Default is 'pass'.\n
    --db-port <PORT>                    Port that the tethys database server will use. Default is 5436.\n
    -S, --superuser <USERNAME>          Tethys super user name. Default is 'admin'.\n
    -E, --superuser-email <EMAIL>       Tethys super user email. Default is ''.\n
    -P, --superuser-pass <PASSWORD>     Tethys super user password. Default is 'pass'.\n
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
LINUX_DISTRIBUTION=$(python -c "import platform; print(platform.linux_distribution(full_distribution_name=0)[0])")
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


# Set default options
ALLOWED_HOST='127.0.0.1'
TETHYS_HOME=~/tethys
TETHYS_PORT=80
TETHYS_DB_USERNAME='tethys_default'
TETHYS_DB_PASSWORD='pass'
TETHYS_DB_HOST='172.17.0.1'
TETHYS_DB_PORT=5432
CONDA_ENV_NAME='tethys'
PYTHON_VERSION='2'

TETHYS_SUPER_USER='admin'
TETHYS_SUPER_USER_EMAIL=''
TETHYS_SUPER_USER_PASS='pass'

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
    --db-port)
    set_option_value TETHYS_DB_PORT "$2"
    shift # past argument
    ;;
    --db-host)
    set_option_value TETHYS_DB_HOST "$2"
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


# Rename some variables for reference after deactivating tethys environment.
TETHYS_CONDA_HOME=${CONDA_HOME}
TETHYS_CONDA_ENV_NAME=${CONDA_ENV_NAME}


# prompt for sudo
echo "Installing Tethys Production Server..."

# NGINEX
rm /etc/nginx/sites-enabled/default
NGINX_SITES_DIR='sites-enabled'

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
echo "unalias tsr" >> "${DEACTIVATE_SCRIPT}"


# ACTIVATE
. ${CONDA_HOME}/bin/activate ${CONDA_ENV_NAME}

# INSTALL REQUIREMENTS
conda install -c conda-forge uwsgi -y

# GEN SETTINGS
tethys gen settings --production --allowed-host=${ALLOWED_HOST} --db-username ${TETHYS_DB_USERNAME} --db-password ${TETHYS_DB_PASSWORD} --db-port ${TETHYS_DB_PORT} --overwrite
sed -i -e "s/'HOST': '127.0.0.1',/'HOST': '${TETHYSBUILD_DB_HOST}',/g" /usr/lib/tethys/src/tethys_portal/settings.py
sed -i -e 's/BYPASS_TETHYS_HOME_PAGE = False/BYPASS_TETHYS_HOME_PAGE = True/g' /usr/lib/tethys/src/tethys_portal/settings.py
sed -i -e "s/#TETHYS_WORKSPACES_ROOT = '\/var\/www\/tethys\/static\/workspaces'/TETHYS_WORKSPACES_ROOT = '\/usr\/lib\/tethys\/workspaces'/g" /usr/lib/tethys/src/tethys_portal/settings.py

sed -i -e 's/SESSION_SECURITY_WARN_AFTER = 840/SESSION_SECURITY_WARN_AFTER = 25 * 60/g' /usr/lib/tethys/src/tethys_portal/settings.py
sed -i -e 's/SESSION_SECURITY_EXPIRE_AFTER = 900/SESSION_SECURITY_EXPIRE_AFTER = 30 * 60/g' /usr/lib/tethys/src/tethys_portal/settings.py

# DB ROLLS/ETC
if [[ $(psql -U postgres -h ${TETHYS_DB_HOST} -p  ${TETHYS_DB_PORT} --command ""; echo $?) -ne 0 ]]; then # Check if postgres has a password
  echo "default postgres user has a password set, assuming database is setup correctly..."
  tethys manage syncdb
else
  if [[ $(psql -U postgres -h ${TETHYS_DB_HOST} -p ${TETHYS_DB_PORT} --command "SELECT 1 FROM pg_roles WHERE rolname='${TETHYS_DB_USERNAME}'" | grep -q 1; echo $?) -ne 0 ]]; then 
    echo "Creating DB User and Password"
    cd /usr/lib/tethys/src
    psql -U postgres -h ${TETHYS_DB_HOST} -p ${TETHYS_DB_PORT} --command "CREATE USER ${TETHYS_DB_USERNAME} WITH NOCREATEDB NOCREATEROLE NOSUPERUSER PASSWORD '${TETHYS_DB_PASSWORD}';"
    createdb -U postgres -h ${TETHYS_DB_HOST} -p ${TETHYS_DB_PORT} -O ${TETHYS_DB_USERNAME} ${TETHYS_DB_USERNAME} -E utf-8 -T template0
    tethys manage syncdb
    echo "from django.contrib.auth.models import User; User.objects.create_superuser('${TETHYS_SUPER_USER}', '${TETHYS_SUPER_USER_EMAIL}', '${TETHYS_SUPER_USER_PASS}')"
    echo "from django.contrib.auth.models import User; User.objects.create_superuser('${TETHYS_SUPER_USER}', '${TETHYS_SUPER_USER_EMAIL}', '${TETHYS_SUPER_USER_PASS}')" | python manage.py shell
    cd /usr/lib/tethys
  else
    tethys manage syncdb
  fi
fi

# NGINX AND UWSGI
tethys gen nginx --overwrite
tethys gen uwsgi_settings --overwrite
tethys gen uwsgi_service --overwrite
NGINX_USER=$(grep 'user .*;' /etc/nginx/nginx.conf | awk '{print $2}' | awk -F';' '{print $1}')
NGINX_GROUP=${NGINX_USER}
NGINX_HOME=$(grep ${NGINX_USER} /etc/passwd | awk -F':' '{print $6}')
chmod 705 ~
mkdir /var/log/uwsgi
touch /var/log/uwsgi/tethys.log
ln -s ${TETHYS_HOME}/src/tethys_portal/tethys_nginx.conf /etc/nginx/${NGINX_SITES_DIR}/
chown -R ${NGINX_USER}:${NGINX_GROUP} ${TETHYS_HOME}/src /var/log/uwsgi/tethys.log

# STATIC FILES AND WORKSPACES
mkdir -p ${TETHYS_HOME}/static ${TETHYS_HOME}/workspaces ${TETHYS_HOME}/apps
tethys manage collectall --noinput
chown -R ${NGINX_USER}:${NGINX_GROUP} ${TETHYS_HOME}

# ECHOING
set +x

# DEACTIVATE
. deactivate


# EXIT
on_exit(){
    set +e
    set +x
}
trap on_exit EXIT

