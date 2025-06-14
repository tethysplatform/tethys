.. _production_file_permissions_config:

****************
File Permissions
****************

**Last Updated:** October 2024

As NGINX is acting as the primary HTTP process, many of the files will need to be accessible by the NGINX user account. There are additional permissions that need to be granted if `Security-Enhanced Linux (SELinux) <https://en.wikipedia.org/wiki/Security-Enhanced_Linux>`_ is active on your server. This part of the production installation guide will show you how to manage the file permissions for your server.

1. Change Static and Workspace Ownership
========================================

Change the owner of the ``STATIC_ROOT`` and ``TETHYS_WORKSPACES_ROOT`` directories and contents to the ``NGINX_USER``:

    .. code-block:: bash

        sudo chown -R <NGINX_USER|APACHE_USER>: <STATIC_ROOT>
        sudo chown -R <NGINX_USER|APACHE_USER>: <TETHYS_WORKSPACES_ROOT>
        sudo chown -R <NGINX_USER|APACHE_USER>: <MEDIA_ROOT>

    .. note::

        Replace ``<NGINX_USER|APACHE_USER>`` with the user noted in the :ref:`production_nginx_config` step. Replace ``<STATIC_ROOT>``, ``<TETHYS_WORKSPACES_ROOT>``, and ``<MEDIA_ROOT>`` with the paths to the directories you set up in the :ref:`production_static_workspaces_dirs` step.

.. _setup_file_permissions_shortcuts:

2. Setup Shortcuts for Changing Permissions (Optional)
======================================================

You will often need to change the ownership of the ``TETHYS_HOME``, ``STATIC_ROOT``, ``MEDIA_ROOT``, and ``TETHYS_WORKSPACES_ROOT`` to your user and then back to the ``nginx`` user again. This needs to be done whenever you are making changes to files in one of these directories. For example, whenever you run ``tethys manage collectstatic``, you will need to change the ownership of these directories to your user to allow the command to copy files into those directories. Then you will need to change it back to the ``nginx`` user to allow the server to have access to these files to serve them.

For convenience, you may consider setting up these or similar aliases in the activate script of your environment:

    .. code-block:: bash

        export ACTIVATE_SCRIPT="<CONDA_HOME>/envs/<CONDA_ENV_NAME>/etc/conda/activate.d/tethys-activate.sh"
        export DEACTIVATE_SCRIPT="<CONDA_HOME>/envs/<CONDA_ENV_NAME>/etc/conda/deactivate.d/tethys-deactivate.sh"
        export STATIC_ROOT="<STATIC_ROOT>"
        export TETHYS_WORKSPACES_ROOT="<TETHYS_WORKSPACES_ROOT>"
        export TETHYS_HOME="<TETHYS_HOME>"
        export NGINX_USER="<NGINX_USER>"

        # Add lines to the activate script that create aliases that change ownership of Tethys directories to the active user
        echo "alias tethys_user_own='sudo chown -R \${USER} \"${STATIC_ROOT}\" \"${TETHYS_WORKSPACES_ROOT}\"'" >> "${ACTIVATE_SCRIPT}"
        echo "alias tuo=tethys_user_own" >> "${ACTIVATE_SCRIPT}"

        # Add lines to the activate script that create aliases that change ownership of Tethys directories to the NGINX user
        echo "alias tethys_server_own='sudo chown -R ${NGINX_USER} \"${STATIC_ROOT}\" \"${TETHYS_WORKSPACES_ROOT}\"'" >> "${ACTIVATE_SCRIPT}"
        echo "alias tso=tethys_server_own" >> "${ACTIVATE_SCRIPT}"

        # Add lines that remove the aliases to the deactivate Script
        echo "unalias tethys_user_own" >> "${DEACTIVATE_SCRIPT}"
        echo "unalias tuo" >> "${DEACTIVATE_SCRIPT}"
        echo "unalias tethys_server_own" >> "${DEACTIVATE_SCRIPT}"
        echo "unalias tso" >> "${DEACTIVATE_SCRIPT}"

1. Copy the lines above into a new shell script (e.g.: :file:`setup_aliases.sh`) and then edit the file, replacing all of the variables in angle brackets (i.e. <CONDA_HOME>) with the appropriate values:

* ``<CONDA_HOME>``: Path to where you installed conda. The default is :file:`/home/<username>/miniconda3` or :file:`~/miniconda3`.
* ``<CONDA_ENV_NAME>``: Name of your Tethys environment. This is usually `tethys` unless you specifically changed it during the :ref:`production_install_tethys` step.
* ``<STATIC_ROOT>``: Path to the directory with the static files that you setup in the :ref:`production_static_workspaces_dirs` step.
* ``<TETHYS_WORKSPACES_ROOT>``: Path to the directory with the app workspaces files that you setup in the :ref:`production_static_workspaces_dirs` step.
* ``<TETHYS_HOME>``: Path to the Tethys home directory that you noted in the :ref:`production_portal_config` step.
* ``<NGINX_USER>``: Name of the NGINX user that you noted in the :ref:`production_nginx_config` step.

.. important::

    Do not replaces the `${}` variables in the script.

2. Deactivate your environment and then run the shell script. For example:

    .. code-block:: bash

        conda deactivate
        . setup_aliases.sh

3. :ref:`activate_environment` and test the commands and check permissions on the directories to verify they worked:

    .. code-block:: bash

        tethys_user_own

4. Be sure to change ownership back to the NGINX user before moving on:

    .. code-block:: bash

        tethys_server_own

.. _selinux_configuration:

3. Security-Enhanced Linux File Permissions (Rocky Linux, May not Apply)
========================================================================

If you are installing Tethys Portal on a Rocky Linux or RedHat system that has `Security-Enhanced Linux (SELinux) <https://en.wikipedia.org/wiki/Security-Enhanced_Linux>`_ enabled and set to enforcing mode, you may need to perform additional setup to allow the server processes to access files.

SELinux adds additional layers of security that define access controls for applications, processes, and files on a system. To learn more about SELinux see: `Security-Enhanced Linux <https://en.wikipedia.org/wiki/Security-Enhanced_Linux>`_, `What is SELinux <https://www.redhat.com/en/topics/linux/what-is-selinux>`_, `CentOS SELinux <https://wiki.centos.org/HowTos(2f)SELinux.html>`_, `RedHat SELinux <https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/5/html/deployment_guide/ch-selinux>`_.

.. note::

    If you are using Rocky Linux for your deployment, it does not necessarily mean that you are using it with SELinux enforcing. You can check the ``SELINUX`` variable in :file:`/etc/selinux/config` to see if SELinux is being enforced. Alternatively, you can check using the ``getenforce`` command.

For an example of SELinux configuration, see: :ref:`production_selinux_config`.