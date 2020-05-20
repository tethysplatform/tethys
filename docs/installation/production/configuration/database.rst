.. _production_database:

*******************
Production Database
*******************

**Last Updated:** May 2020

 * Set Database Parameters:

        .. code-block::

            tethys settings --set DATABASES.default.USER <TETHYS_DB_USERNAME> --set DATABASES.default.PASSWORD <TETHYS_DB_PASSWORD> --set DATABASES.default.HOST <TETHYS_DB_HOST> --set DATABASES.default.PORT <TETHYS_DB_PORT>

        .. important::

            Do not use the default username or password for the production Tethys database. Also ensure the host and port match the host and port that your database is running on.

    * Disable Debug:

        .. code-block::

            tethys settings --set DEBUG False

6) Setup Tethys Database:

    Create the Tethys Database using the ``tethys db`` command (see :ref:`tethys_db_cmd`):

    .. code-block::

        tethys db configure --username <TETHYS_DB_USERNAME> --password <TETHYS_DB_PASSWORD> --superuser-name <TETHYS_DB_SUPER_USERNAME> --superuser-password <TETHYS_DB_SUPER_PASSWORD> --portal-superuser-name <TETHYS_SUPER_USER> --portal-superuser-email '<TETHYS_SUPER_USER_EMAIL>' --portal-superuser-pass <TETHYS_SUPER_USER_PASS>

    .. tip::

        The ``TETHYS_DB_USERNAME`` and ``TETHYS_DB_PASSWORD`` need to be the same as those set in the portal config (see pervious step).

    .. note::

        Running ``tethys db configure`` is equivalent of running the following commands:

        * ``tethys db init`` (skip if using a Docker or system database)
        * ``tethys db start`` (skip if using a Docker or system database)
        * ``tethys db create --username <TETHYS_DB_USERNAME> --password <TETHYS_DB_PASSWORD> --superuser-name <TETHYS_DB_SUPER_USERNAME> --superuser-password <TETHYS_DB_SUPER_PASSWORD>``
        * ``tethys db migrate``
        * ``tethys db createsuperuser --portal-superuser-name <TETHYS_SUPER_USER> --portal-superuser-email '<TETHYS_SUPER_USER_EMAIL>' --portal-superuser-pass <TETHYS_SUPER_USER_PASS>``

    .. tip::

        You need to prepend the ``tethys db`` commands with the password for the postgres user of the database when using a Docker or a system install:

        .. code-block:: bash

            $ PGPASSWORD="<POSTGRES_PASSWORD>" tethys db configure --username <USERNAME> --password <TETHYS_DB_PASSWORD> --superuser-name <TETHYS_DB_SUPER_USERNAME> --superuser-password <TETHYS_DB_SUPER_PASSWORD> --portal-superuser-name <TETHYS_SUPER_USER> --portal-superuser-email '<TETHYS_SUPER_USER_EMAIL>' --portal-superuser-pass <TETHYS_SUPER_USER_PASS>