.. _docker_build:

******************
Build Docker Image
******************

**Last Updated:** February 2023

With the :file:`Dockerfile` and Salt State scripts complete, the custom Docker image can now be built. Change back into the :file:`tethys_portal_docker` directory if necessary and run the command:

.. code-block:: bash

    docker build -t tethys-portal-docker .

.. note::

    The ``-t`` option is used name or tag the docker image. The name can have two parts, separated by a ``:``: ``<name>:<tag>``. If a ``<tag>`` isn't given, it defaults to ``latest``.

Run the following command to verify that the image was created:

.. code-block:: bash

    docker images

You should see an image with a repository "tethys-portal-docker" and tag "latest" in the list of images similar to this:

.. code-block:: bash

    REPOSITORY             TAG       IMAGE ID       CREATED          SIZE
    tethys-portal-docker   latest    426b6a6f36c5   1 minute ago   2.31GB

Solution
========

A working build of the ``tethys-portal-docker`` image is available on Docker Hub here: `<https://hub.docker.com/repository/docker/tethysplatform/tethys-portal-docker>`_.

What's Next?
============

Continue to the next tutorial to learn how to run the built image using Docker Compose.