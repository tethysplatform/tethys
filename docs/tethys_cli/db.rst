.. _tethys_db_cmd:

db command
**********

Setup and manage a Tethys database.

.. important::

    The default database configuration uses SQLite. Many of these commands are not applicable to SQLite databases and only support PostgreSQL databases. To use a PostgreSQL database be sure to set your settings accordingly. At the very least:

    .. code-block:: bash

        tethys settings --set DATABASES.default.ENGINE django.db.backends.postgresql

    For more details see :ref:`database_configuration`

    Additionally, the PostgreSQL database and the ``psycopg2`` library must be installed. Starting with Tethys 5.0 or if you are using ``micro-tethys-platform``, you will need to install ``postgresql`` and ``psycopg2`` using conda as follows:

    .. code-block:: bash

        # conda: conda-forge channel strongly recommended
        conda install -c conda-forge postgresql psycopg2

.. argparse::
   :module: tethys_cli
   :func: tethys_command_parser
   :prog: tethys
   :path: db