export CONDA_SCRIPTS_DIR=$CONDA_PREFIX/etc/conda/
export ACTIVATE_SCRIPT_DIR=$CONDA_SCRIPTS_DIR/activate.d
export DEACTIVATE_SCRIPT_DIR=$CONDA_SCRIPTS_DIR/deactivate.d

export ACTIVATE_SCRIPT=$ACTIVATE_SCRIPT_DIR/tethys-activate.sh
export DEACTIVATE_SCRIPT=$DEACTIVATE_SCRIPT_DIR/tethys-deactivate.sh
export STATIC_ROOT=~/.tethys/static
export TETHYS_WORKSPACES_ROOT=~/.tethys/workspaces
export TETHYS_HOME=~/.tethys
export NGINX_USER=nginx
export PORT="${PORT:-8000}"
export HOSTNAME=127.0.0.1

if [ "${CONDA_ENV_NAME}" != "tethys" ]
then
  TETHYS_HOME=${TETHYS_HOME}/$CONDA_DEFAULT_ENV
fi

mkdir -p ${ACTIVATE_SCRIPT_DIR}
mkdir -p ${DEACTIVATE_SCRIPT_DIR}
touch ${ACTIVATE_SCRIPT}
touch ${DEACTIVATE_SCRIPT}

mkdir -p ${TETHYS_HOME}
ln -s ${ACTIVATE_SCRIPT} ${TETHYS_HOME}/tethys-activate.sh
ln -s ${DEACTIVATE_SCRIPT} ${TETHYS_HOME}/tethys-deactivate.sh

# Add lines to the activate script that create an alias to easily edit the portal_config.yml file for this environment
echo "export TETHYS_HOME=${TETHYS_HOME}" > "${ACTIVATE_SCRIPT}"
echo "alias vipc='vi ${TETHYS_HOME}/portal_config.yml'" >> "${ACTIVATE_SCRIPT}"
# Add lines to the activate script that create aliases to start the tethys development server
echo "alias tms='tethys manage start -p ${HOSTNAME}:${PORT}'" >> "${ACTIVATE_SCRIPT}"
echo "alias tstart='tethys db start; tms'"  >> "${ACTIVATE_SCRIPT}"
# Add lines to the activate script that create aliases that change ownership of Tethys directories to the active user
echo "alias tethys_user_own='sudo chown -R \${USER} \"${STATIC_ROOT}\" \"${TETHYS_WORKSPACES_ROOT}\"'" >> "${ACTIVATE_SCRIPT}"
echo "alias tuo=tethys_user_own" >> "${ACTIVATE_SCRIPT}"
# Add lines to the activate script that create aliases that change ownership of Tethys directories to the NGINX user
echo "alias tethys_server_own='sudo chown -R ${NGINX_USER} \"${STATIC_ROOT}\" \"${TETHYS_WORKSPACES_ROOT}\"'" >> "${ACTIVATE_SCRIPT}"
echo "alias tso=tethys_server_own" >> "${ACTIVATE_SCRIPT}"
echo "alias cs='tuo; tethys manage collectstatic; tso;'" >> "${ACTIVATE_SCRIPT}"
echo "alias tsr='tso; sudo systemctl restart supervisord'" >> "${ACTIVATE_SCRIPT}"
# Add lines that remove the aliases to the deactivate Script
echo "unset TETHYS_HOME" > "${DEACTIVATE_SCRIPT}"
echo "unalias vipc" > "${DEACTIVATE_SCRIPT}"
echo "unalias tethys_user_own" > "${DEACTIVATE_SCRIPT}"
echo "unalias tuo" >> "${DEACTIVATE_SCRIPT}"
echo "unalias tethys_server_own" >> "${DEACTIVATE_SCRIPT}"
echo "unalias tso" >> "${DEACTIVATE_SCRIPT}"
echo "unalias cs" >> "${DEACTIVATE_SCRIPT}"
echo "unalias tsr" >> "${DEACTIVATE_SCRIPT}"

source ${ACTIVATE_SCRIPT}
