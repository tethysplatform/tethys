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
export NGINX_PIDFILE=$(grep 'pid .*;' /etc/nginx/nginx.conf | awk '{print $2}' | awk -F';' '{print $1}')
export ASGI_PIDFILE=$(grep 'pidfile=.*' /etc/supervisor/supervisord.conf | awk -F'=' '{print $2}' | awk '{print $1}')

# Create Salt Config
echo "file_client: local" > /etc/salt/minion 
echo "postgres.host: '${TETHYS_DB_HOST}'" >> /etc/salt/minion 
echo "postgres.port: '${TETHYS_DB_PORT}'" >> /etc/salt/minion
echo "postgres.user: '${TETHYS_DB_USERNAME}'" >> /etc/salt/minion 
echo "postgres.pass: '${TETHYS_DB_PASSWORD}'" >> /etc/salt/minion 
echo "postgres.bins_dir: '${CONDA_HOME}/envs/${CONDA_ENV_NAME}/bin'" >> /etc/salt/minion 

# Apply States
echo_status "Enforcing start state... (This might take a bit)"
salt-call --local state.apply
echo_status "Fixing permissions"
find ${TETHYS_HOME} ! -user ${NGINX_USER} -print0 | xargs -0 -I{} chown ${NGINX_USER}: {}

echo_status "Starting supervisor"

# Create NGINX Supervisor Config
echo "[program:nginx]" >> /etc/supervisor/conf.d/nginx_supervisord.conf
echo "command=/usr/sbin/nginx -g 'daemon off;'" >> /etc/supervisor/conf.d/nginx_supervisord.conf
echo "stdout_logfile=/var/log/nginx/access.log" >> /etc/supervisor/conf.d/nginx_supervisord.conf
echo "stderr_logfile=/var/log/nginx/error.log" >> /etc/supervisor/conf.d/nginx_supervisord.conf
echo "redirect_stderr=true" >> /etc/supervisor/conf.d/nginx_supervisord.conf

# Start Supervisor
/usr/bin/supervisord -n

echo_status "Done!"

# Watch Logs
echo_status "Watching logs"
tail -qF /var/log/supervisor/* /var/log/nginx/* /var/log/asgi/*
