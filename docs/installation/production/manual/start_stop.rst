.. _production_start_stop:

****************
Start the Server
****************

**Last Updated:** September 2022

The Tethys Portal production deployment uses NGINX and Daphne servers. Rather than manage these processes individually, you should use the ``supervisorctl`` command to perform start, stop, and restart operations:

    Start:

    .. code-block::

        sudo supervisorctl start all

    Stop:

    .. code-block::

        sudo supervisorctl stop all

    Restart:

    .. code-block::

        sudo supervisorctl restart all

You can also start, stop, or restart nginx:

    .. code-block::

        sudo supervisorctl restart nginx

You can also start, stop, and restart all of the the Daphne processes:

    .. code-block::

        sudo supervisorctl restart asgi:*
