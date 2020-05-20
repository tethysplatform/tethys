.. _production_file_permissions_config:

****************
File Permissions
****************

**Last Updated:** May 2020

14) Change Permissions of Tethys Directories

    Many of the directories and files need to be owned by the ``nginx`` user for Tethys to access them while running in production.

    .. code-block::

        sudo chown -R <NGINX_USER>: <STATIC_ROOT>
        sudo chown -R <NGINX_USER>: <TETHYS_WORKSPACE_ROOT>

    .. note::

        Replace ``<NGINX_USER>`` with the user noted in step 9.

    Change access to the home directory to full access for owners, no access for group, and read execute for other:

    .. code-block::

        sudo chmod 705 ~

    .. tip::

        You will often need to change the permissions of ``TETHYS_HOME``, ``STATIC_ROOT``, and ``TETHYS_WORKSPACES_ROOT`` to your user and back to the ``nginx`` user when performing maintenance operations. Define these aliases in the activate script of your environment to make it easier:

        .. code-block::

            export ACTIVATE_SCRIPT="<CONDA_HOME>/envs/<CONDA_ENV_NAME>/etc/conda/activate.d/tethys-activate.sh"
            export DEACTIVATE_SCRIPT="<CONDA_HOME>/envs/<CONDA_ENV_NAME>/etc/conda/deactivate.d/tethys-deactivate.sh"
            export STATIC_ROOT="<STATIC_ROOT>"
            export TETHYS_WORKSPACE_ROOT="<TETHYS_WORKSPACE_ROOT>"
            export TETHYS_HOME="<TETHYS_HOME>"
            export NGINX_USER="<NGINX_USER>"

            echo "alias tethys_user_own='sudo chown -R \${USER} \"${TETHYS_SRC}\" \"${TETHYS_HOME}/static\" \"${TETHYS_HOME}/workspaces\" \"${TETHYS_HOME}/apps\"'" >> "${ACTIVATE_SCRIPT}"
            echo "alias tuo=tethys_user_own" >> "${ACTIVATE_SCRIPT}"
            echo "alias tethys_server_own='sudo chown -R ${NGINX_USER}: \"${TETHYS_SRC}\" \"${TETHYS_HOME}/static\" \"${TETHYS_HOME}/workspaces\" \"${TETHYS_HOME}/apps\"'" >> "${ACTIVATE_SCRIPT}"
            echo "alias tso=tethys_server_own" >> "${ACTIVATE_SCRIPT}"
            echo "alias tethys_server_restart='tso; sudo supervisorctl restart all;'" >> "${ACTIVATE_SCRIPT}"
            echo "alias tsr=tethys_server_restart" >> "${ACTIVATE_SCRIPT}"

            echo "unalias tethys_user_own" >> "${DEACTIVATE_SCRIPT}"
            echo "unalias tuo" >> "${DEACTIVATE_SCRIPT}"
            echo "unalias tethys_server_own" >> "${DEACTIVATE_SCRIPT}"
            echo "unalias tso" >> "${DEACTIVATE_SCRIPT}"
            echo "unalias tethys_server_restart" >> "${DEACTIVATE_SCRIPT}"
            echo "unalias tsr" >> "${DEACTIVATE_SCRIPT}"