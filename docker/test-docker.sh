#!/bin/bash

echo_status() {
  local args="${@}"
  tput setaf 4
  tput bold
  echo -e "- $args"
  tput sgr0
}

echo_status "Starting up..."

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
