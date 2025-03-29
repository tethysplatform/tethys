.. _docker_get_started:

***************************
Getting Started with Docker
***************************

**Last Updated:** November 2021

To get started using Docker, you'll first need to install it. Docker provide excellent documentation for installation that can be found here: `Get Docker | Docker Documentation <https://docs.docker.com/get-started/get-docker/>`_. This guide provides shortcuts to installation instructions that are most relevant to Tethys app developers.

Install
=======

Use the appropriate instructions below to install Docker:

Linux
-----

Docker provides `installation instructions for the most popular Linux distributions <https://docs.docker.com/engine/install/>`_ including (CentOS, Debian, Fedora, Raspbian, RHEL, SLES, and Ubuntu). It should be possible to install it on other Linux distributions. As we recommend deploying Tethys Platform on either CentOS or Ubuntu, links to the installation instructions for these two distributions are provided below:

* `Install Docker Engine on CentOS | Docker Documentation <https://docs.docker.com/engine/install/centos/>`_
* `Install Docker Engine on Ubuntu | Docker Documentation <https://docs.docker.com/engine/install/ubuntu/>`_

Notes:

* We recommend using the **Install using the repository** method.
* If you intend to use the ``tethys docker`` command or if you'd like to use it without ``sudo``, you'll need to complete the `Manage Docker as a non-root user <https://docs.docker.com/engine/install/linux-postinstall/#manage-docker-as-a-non-root-user>`_ post-installation step as well.

Windows and Mac
---------------

On Windows and Mac you will install Docker Desktop, which provides a graphical user interface for Docker (Figure 1). It also includes the commandline Docker client and on Windows you have the ability to switch between running Linux and Windows docker containers.

.. figure:: images/install--docker-desktop.png
    :width: 800px
    :alt: Screenshot of Docker Desktop on Windows.

    **Figure 1**: Screenshot of Docker Desktop on Windows.

Use one of the links below to install Docker Desktop on Windows or Mac:

* `Install Docker Desktop for Windows <https://docs.docker.com/desktop/setup/install/windows-install/>`_
* `Install Docker Desktop for Mac <https://docs.docker.com/desktop/setup/install/mac-install/>`_

Verify Installation
===================

After installing Docker Desktop, you should be able to use the ``docker`` command on the command prompt/terminal as you would in Linux. Create the ``docker/getting-started`` container to verify the installation as follows:

.. code-block::

    docker run -d -p 80:80 docker/getting-started

.. note::

    When you run a container, the Docker daemon automatically assigns the container a random human readable name of the form ``<adjective>_<noun>``. For example "angry_grothendieck". You can also specify a name using the ``--name`` option. Just remember that the name needs to be unique among the containers running on your system.

    .. code-block::

        docker run --name my_first_container -d -p 80:80 docker/getting-started

The ``docker run`` command will automatically pull (download) the ``docker/getting-started`` image if it hasn't been pulled already and then create and start the container. The ``docker/getting-started`` image contains a website with a tutorial for Docker (Figure 2). To view the tutorial open a web browser and navigate to `<http://localhost>`_.

.. figure:: images/install--getting-started.png
    :width: 800px
    :alt: Screenshot of the Getting Started tutorial website running in the getting-started container.

    **Figure 2**: Screenshot of the Getting Started tutorial website running in the getting-started container.

Tutorial
========

If you are new to Docker, we highly recommend completing the Getting Started tutorial that is now running Docker (see previous step). You can also access the tutorial on Docker's website: `Orientation and setup | Docker Documentation <https://docs.docker.com/get-started/>`_. In this tutorial you will learn the following important concepts:

* `Building Docker Images <https://docs.docker.com/get-started/workshop/02_our_app/#build-the-apps-image>`_
* `Running Docker Containers <https://docs.docker.com/get-started/workshop/02_our_app/#start-an-app-container>`_
* `Managing Docker Containers <https://docs.docker.com/get-started/workshop/03_updating_app/>`_
* `Publishing Docker Images on Docker Hub <https://docs.docker.com/get-started/workshop/04_sharing_app/>`_
* `Persisting Container Data with Volumes <https://docs.docker.com/get-started/workshop/05_persisting_data/>`_
* `Mounting Directories into Containers <https://docs.docker.com/get-started/workshop/06_bind_mounts/>`_
* `Multiple Container Apps <https://docs.docker.com/get-started/workshop/07_multi_container/>`_
* `Docker Compose <https://docs.docker.com/get-started/workshop/08_using_compose/>`_
* `Image Building Best Practices <https://docs.docker.com/get-started/workshop/09_image_best/>`_
