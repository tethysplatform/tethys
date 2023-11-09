#!/bin/bash

echo_status() {
  local args="${@}"
  tput setaf 4
  tput bold
  echo -e "- $args"
  tput sgr0
}

db_max_count=24;
USAGE="USAGE: . run.sh [options]
OPTIONS:
--db-max-count <INT>      \t number of attempt to connect to the database. Default is at 24.
"

while [[ $# -gt 0 ]]; do
  case $1 in
    --db-max-count)
      shift # shift from key to value
      db_max_count=$1;
    ;;
    *)
      echo -e "${USAGE}"
      return 0
  esac
  shift
done

echo_status "Starting up..."

if [ ! -f "$TETHYS_HOME/portal_config.yml" ]; then
    echo_status "Generating portal config..."
    tethys gen portal_config
fi

# Set extra ENVs
export NGINX_USER=$(grep 'user .*;' /etc/nginx/nginx.conf | awk '{print $2}' | awk -F';' '{print $1}')

if [[!-z "$TETHYS_DB_HOST" ]] && [[!-z "$TETHYS_DB_PORT" ]]; then
    # Set db settings
    tethys settings --set DATABASES.default.ENGINE django.db.backends.postgresql \
                    --set DATABASES.default.NAME tethys_platform \
                    --set DATABASES.default.USER ${TETHYS_DB_USERNAME} \
                    --set DATABASES.default.PASSWORD ${TETHYS_DB_PASSWORD} \
                    --set DATABASES.default.HOST ${TETHYS_DB_HOST} \
                    --set DATABASES.default.PORT ${TETHYS_DB_PORT}

    # Wait until db starts
    echo_status "Waiting for db to be ready..."

    db_check_count=0

    until ${CONDA_HOME}/envs/${CONDA_ENV_NAME}/bin/pg_isready -h ${TETHYS_DB_HOST} -p ${TETHYS_DB_PORT} -U postgres; do
    if [[ $db_check_count -gt $db_max_count ]]; then
        >&2 echo "DB was not available in time - exiting"
        exit 1
    fi
    >&2 echo "DB is unavailable - sleeping"
    db_check_count=`expr $db_check_count + 1`
    sleep 5
    done

    echo_status "DB is ready"
fi

echo_status "Initializing database..."
if [[!-z "$TETHYS_DB_HOST" ]] && [[!-z "$TETHYS_DB_PORT" ]]; then
    PGPASSWORD=${POSTGRES_PASSWORD} tethys db configure
else
    tethys db configure
fi

# Start tethys dev server
echo_status "Starting tethys"
tethys manage start -p 0.0.0.0:8000

