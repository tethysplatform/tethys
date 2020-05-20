.. _production_supervisor_config:

*********************************
Supervisor & Daphne Configuration
*********************************

**Last Updated:** May 2020

12) Generate ``nginx`` and ``supervisor`` Configuration Files:

    Generate and review the contents of the following configuration files for ``nginx`` and ``supervisor``. Adjust to match your deployment's needs if necessary.

    .. code-block::

        tethys gen nginx --overwrite
        tethys gen nginx_service --overwrite
        tethys gen asgi_service --overwrite

    .. tip::

        These files are generated in the ``TETHYS_HOME`` directory.



9) Note ``nginx`` User for Permissions


    Get the ``nginx`` user for permissions changes in the follow steps.

    .. code-block::

        grep 'user .*;' /etc/nginx/nginx.conf | awk '{print $2}' | awk -F';' '{print $1}'

    Note this user and use it in the following steps where you see ``<NGINX_USER>``.

10) Setup Log File

    This is the file to which Tethys logs will be written.

    .. code-block::

        sudo mkdir -p /var/log/tethys
        sudo touch /var/log/tethys/tethys.log

    .. code-block::

        sudo chown -R <NGINX_USER>: /var/log/tethys

    .. note::

        Replace ``<NGINX_USER>`` with the user noted in step 9.

11) Setup ASGI Run Directory

    This directory is used for housing the socket files for the Daphne/ASGI processes.

    .. code-block::

        sudo mkdir -p /run/asgi

    .. code-block::

        sudo chown -R <NGINX_USER>: /run/asgi

    .. note::

        Replace ``<NGINX_USER>`` with the user noted in step 9.

13) Configure ``nginx`` and ``supervisor`` to Use Tethys Configurations:

    Creates symbolic links to configuration file in the appropriate ``/etc`` directories:

    Debian and Ubuntu:

    .. code-block::

        sudo ln -s <TETHYS_HOME>/asgi_supervisord.conf /etc/supervisor/conf.d/asgi_supervisord.conf
        sudo ln -s <TETHYS_HOME>/nginx_supervisord.conf /etc/supervisor/conf.d/nginx_supervisord.conf
        sudo ln -s <TETHYS_HOME>/tethys_nginx.conf /etc/nginx/sites-enabled/tethys_nginx.conf

        # Remove the default nginx configuration
        sudo rm /etc/nginx/sites-enabled/default

    Fedora, CentOS, RedHat

    .. code-block::

        sudo sed -i '$ s@$@ /etc/supervisord.d/*.conf@' "/etc/supervisord.conf"
        sudo ln -s <TETHYS_HOME>/asgi_supervisord.conf /etc/supervisord.d/asgi_supervisord.conf
        sudo ln -s <TETHYS_HOME>/nginx_supervisord.conf /etc/supervisord.d/nginx_supervisord.conf
        sudo ln -s <TETHYS_HOME>/tethys_nginx.conf /etc/nginx/conf.d/tethys_nginx.conf