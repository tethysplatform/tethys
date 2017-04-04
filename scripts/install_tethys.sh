#!/bin/bash

# prompt for sudo
sudo echo "Starting Tethys Installation..."

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
    exit 1
fi

# TODO make these commandline options
TETHYS_DB_PORT=5435
CONDA_HOME="${TETHYS_HOME}/miniconda"
BRANCH=dev

TETHYS_SUPER_USER=admin
TETHYS_SUPER_USER_EMAIL=''
TETHYS_SUPER_USER_PASS=pass

sudo mkdir -p ${TETHYS_HOME}
sudo chown ${USER} ${TETHYS_HOME}

# install miniconda
${MINICONDA_URL} "${TETHYS_HOME}/miniconda.sh"
sudo bash "${TETHYS_HOME}/miniconda.sh" -b -p "${CONDA_HOME}"
sudo chmod -R o+w "${CONDA_HOME}"
export PATH="${CONDA_HOME}/bin:$PATH"

# clone Tethys repo
conda install --yes git
git clone https://github.com/tethysplatform/tethys "${TETHYS_HOME}/src"
cd "${TETHYS_HOME}/src"
git checkout ${BRANCH}

# create conda env and install Tethys
conda env create -f tethys_conda_env.yml
. activate tethys
python setup.py develop
tethys gen settings -d "${TETHYS_HOME}/src/tethys_apps"

# Setup local database
conda install --yes -c conda-forge postgresql
initdb  -U postgres -D "${TETHYS_HOME}/psql/data"
pg_ctl -U postgres -D "${TETHYS_HOME}/psql/data" -l "${TETHYS_HOME}/psql/logfile" start -o "-p ${TETHYS_DB_PORT}"
echo 'wating for databases to startup...'; sleep 10
psql -U postgres -p ${TETHYS_DB_PORT} --command "CREATE USER tethys_default WITH NOCREATEDB NOCREATEROLE NOSUPERUSER PASSWORD 'pass';"
createdb -U postgres -p ${TETHYS_DB_PORT} -O tethys_default tethys_default -E utf-8 -T template0

# Initialze Tethys database
tethys manage syncdb
echo "from django.contrib.auth.models import User; User.objects.create_superuser('${TETHYS_SUPER_USER}', '${TETHYS_SUPER_USER_EMAIL}', '${TETHYS_SUPER_USER_PASS}')" | python manage.py shell

# setup shortcuts and aliases
echo "# Tethys Platform" >> ~/${BASH_PROFILE}
echo "alias t='. ${CONDA_HOME}/bin/activate tethys'" >> ~/${BASH_PROFILE}
. ~/${BASH_PROFILE}

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
echo "alias tms='tethys manage start -p 127.0.0.1:\${TETHYS_PORT}'" >> ${ACTIVATE_SCRIPT}

. ${ACTIVATE_SCRIPT}

echo "unset TETHYS_HOME" >> ${DEACTIVATE_SCRIPT}
echo "unset TETHYS_PORT" >> ${DEACTIVATE_SCRIPT}
echo "unset TETHYS_DB_PORT" >> ${DEACTIVATE_SCRIPT}
echo "unalias tethys_start_db" >> ${DEACTIVATE_SCRIPT}
echo "unalias tstartdb" >> ${DEACTIVATE_SCRIPT}
echo "unalias tms" >> ${DEACTIVATE_SCRIPT}


if [ "$(uname)" = "Linux" -a "${INSTALL_DOCKER}" = "true" ]
then
     sudo apt-key adv --keyserver hkp://p80.pool.sks-keyservers.net:80 --recv-keys 58118E89F3A912897C070ADBF76221572C52609D
     echo "deb https://apt.dockerproject.org/repo ubuntu-$(lsb_release -c | awk '{print $2}') main" | sudo tee /etc/apt/sources.list.d/docker.list
     sudo apt-get update
     sudo apt-get install -y docker-engine
     sudo gpasswd -a ${USER} docker
     sudo service docker restart
     sg docker -c "tethys docker init -d"
     sg docker -c "tethys docker start -c postgis"
     echo 'wating for databases to startup...'; sleep 10
     newgrp docker
fi
