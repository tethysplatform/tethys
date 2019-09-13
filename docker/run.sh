#!/bin/bash

echo_status() {
  local args="${@}"
  tput setaf 4
  tput bold
  echo -e "- $args"
  tput sgr0
}

echo_status "Starting up..."

# Set extra ENVs
export NGINX_USER=$(grep 'user .*;' /etc/nginx/nginx.conf | awk '{print $2}' | awk -F';' '{print $1}')

# Create Salt Config
echo "file_client: local" > /etc/salt/minion 
echo "postgres.host: '${TETHYS_DB_HOST}'" >> /etc/salt/minion 
echo "postgres.port: '${TETHYS_DB_PORT}'" >> /etc/salt/minion
echo "postgres.user: '${TETHYS_DB_USERNAME}'" >> /etc/salt/minion 
echo "postgres.pass: '${TETHYS_DB_PASSWORD}'" >> /etc/salt/minion 
echo "postgres.bins_dir: '${CONDA_HOME}/envs/${CONDA_ENV_NAME}/bin'" >> /etc/salt/minion 

# Apply States
echo_status "Checking if DB is ready"
db_check_count=0
until ${CONDA_HOME}/envs/${CONDA_ENV_NAME}/bin/pg_isready -h ${TETHYS_DB_HOST} -p ${TETHYS_DB_PORT} -U postgres; do
  if [ $db_check_count -gt 24 ]; then
    >&2 echo "DB was not available in time - exiting"
    exit
  fi
  >&2 echo "DB is unavailable - sleeping"
  db_check_count=`expr $db_check_count + 1`
  sleep 5
done
echo_status "Enforcing start state... (This might take a bit)"
salt-call --local state.apply
echo_status "Fixing permissions"
find ${TETHYS_HOME} ! -user ${NGINX_USER} -print0 | xargs -0 -I{} chown ${NGINX_USER}: {}

echo_status "Starting supervisor"

# Start Supervisor
/usr/bin/supervisord -n

echo_status "Done!"

# Watch Logs
echo_status "Watching logs"
tail -qF /var/log/supervisor/* /var/log/nginx/* /var/log/tethys/*
