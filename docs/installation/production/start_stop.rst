.. _production_start_stop:

****************
Start the Server
****************

**Last Updated:** May 2020

Reload the Configuration
========================

Once you have finished the configuration steps, it is necessary to instruct Supervisor to reread and update as follows so that it loads our new Supervisor configurations:

    .. code-block::

        sudo supervisorctl reread
        sudo supervisorctl update

    .. note::

        This step needs to be performed anytime you make changes to the ``nginx_supervisord.conf`` or ``asgi_supervisord.conf``

Future Starting and Stopping
============================

The Tethys Portal production deployment uses NGINX and Daphne servers. Rather than manage these processes individually, you should use the ``supervisorctl`` command to perform start, stop, and restart operations:

    Start:

    .. code-block::

        sudo supervisorctl start

    Stop:

    .. code-block::

        sudo supervisorctl stop

    Restart:

    .. code-block::

        sudo supervisorctl restart
