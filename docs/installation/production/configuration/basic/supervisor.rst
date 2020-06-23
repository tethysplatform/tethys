.. _production_supervisor_config:

*********************************
Supervisor & Daphne Configuration
*********************************

**Last Updated:** May 2020

`Supervisor <http://supervisord.org/>`_ is used to manage the NGINX and Daphne processes. As an ASGI server, Daphne is able to be run with multiple worker processes. It would be cumbersome to manage them individually. Using Supervisor, you will be able to use one command to start, stop, or restart the NGINX process and all of the Daphne processes.

1. Generate the Supervisor Configuration Files
==============================================

One configuration file will be needed for NGINX and another for Daphne. Use the ``tethys gen`` command to generate default versions of these configuration files:

    .. code-block:: bash

        tethys gen nginx_service --overwrite
        tethys gen asgi_service --overwrite


2. Review Supervisor Configuration Files
========================================

1. Review the contents of the NGINX configuration file:

    .. code-block:: bash

        vim <TETHYS_HOME>/nginx_supervisord.conf

    In particular, the locations of the log files. These may be useful for debugging later on.

2. Review the contents of the Daphne (ASGI) configuration file:

    .. code-block:: bash

        vim <TETHYS_HOME>/asgi_supervisord.conf

    In particular, verify the following:

        * The ``TETHYS_HOME`` variable is set correctly
        * The ``directory`` is the path to the directory where Tethys Platform is installed (usually the :file:`site-packages` directory of your ``tethys`` conda environment).
        * Adjust the ``numprocs`` to the number of Daphne processes you would like it to run.
        * Note the location of the ``stdout_logfile``.


.. tip::

    Replace ``<TETHYS_HOME>`` with the path to the Tethys home directory as noted in :ref:`production_portal_config` section.

3. Link the Tethys Supervisor Configuration Files
=================================================

Create a symbolic links from the two configuration files generated in the previous steps to the supervisor configuration directory (:file:`/etc/supervisor`):

    **Ubuntu**:

        .. code-block:: bash

            sudo ln -s <TETHYS_HOME>/asgi_supervisord.conf /etc/supervisor/conf.d/asgi_supervisord.conf
            sudo ln -s <TETHYS_HOME>/nginx_supervisord.conf /etc/supervisor/conf.d/nginx_supervisord.conf

    **CentOS**:

        .. code-block:: bash

            sudo ln -s <TETHYS_HOME>/asgi_supervisord.conf /etc/supervisord.d/asgi_supervisord.conf
            sudo ln -s <TETHYS_HOME>/nginx_supervisord.conf /etc/supervisord.d/nginx_supervisord.conf

    .. tip::

        Replace ``<TETHYS_HOME>`` with the path to the Tethys home directory as noted in :ref:`production_portal_config` section.

4. Modify :file:`supervisord.conf` (CentOS Only)
================================================

For CentOS systems, modify :file:`supervisord.conf` to recognize our configuration files:

    **CentOS**:

        .. code-block:: bash

            sudo sed -i '$ s@$@ /etc/supervisord.d/*.conf@' "/etc/supervisord.conf"

5. Setup Tethys Log
===================

Create the log file in the location where supervisor expects it to be (see last item in 2.2).

1. Create a directory and file for Daphne/Django to write the Tethys Portal logs:

    .. code-block:: bash

        sudo mkdir -p /var/log/tethys
        sudo touch /var/log/tethys/tethys.log

2. Change the directory to be owned by the NGINX user:

    .. code-block:: bash

        sudo chown -R <NGINX_USER> /var/log/tethys

    .. tip::

        Replace ``<NGINX_USER>`` with the name of the user noted in the :ref:`production_nginx_config`.

6. Reload the Configuration
===========================

Once you have finished the configuration steps, it is necessary to instruct Supervisor to reread and update as follows so that it loads our new Supervisor configurations:

    .. code-block::

        sudo supervisorctl reread
        sudo supervisorctl update

    .. note::

        This step needs to be performed anytime you make changes to the ``nginx_supervisord.conf`` or ``asgi_supervisord.conf``
