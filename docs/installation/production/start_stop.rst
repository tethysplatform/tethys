.. _production_start_stop:

***************************************
Starting and Stopping Production Server
***************************************

**Last Updated:** May 2020

15) Reload and Update ``supervisor`` configuration:

    .. code-block::

        sudo supervisorctl reread
        sudo supervisorctl update

    .. note::

        This step needs to be performed anytime you make changes to the ``nginx_supervisord.conf`` or ``asgi_supervisord.conf``