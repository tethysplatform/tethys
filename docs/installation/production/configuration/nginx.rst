.. _production_nginx_config:

*******************
NGINX Configuration
*******************

**Last Updated:** May 2020

12) Generate ``nginx`` and ``supervisor`` Configuration Files:

    Generate and review the contents of the following configuration files for ``nginx`` and ``supervisor``. Adjust to match your deployment's needs if necessary.

    .. code-block::

        tethys gen nginx --overwrite
        tethys gen nginx_service --overwrite
        tethys gen asgi_service --overwrite

    .. tip::

        These files are generated in the ``TETHYS_HOME`` directory.

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