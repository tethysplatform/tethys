**************
THREDDS Primer
**************

**Last Updated:** December 2019

In this tutorial you will discover a brief overview of THREDDS using the Docker container that is included with Tethys Platform:

* Tethys Docker Containers
* THREDDS

1. Start the THREDDS Docker
===========================

1. Initialize the THREDDS Docker container:

.. code-block:: bash

    tethys docker init -c thredds

.. note::

    The command ``tethys docker init`` only needs to be run the first time you are creating a container. If it already exists, you can skip to the next step.


2. Start the THREDDS Docker container:

.. code-block:: bash

    tethys docker start -c thredds

.. tip::

    To stop the docker container:

    .. code-block:: bash

        tethys docker stop -c thredds

    For more information about the Docker interface in Tethys Platform see the :ref:`tethys_cli_docker` reference.

3. Obtain the endpoint for the THREDDS Docker container:

.. code-block:: bash

    tethys docker ip

.. tip::

    Alternatively, you may use an existing THREDDS server for this tutorial.
