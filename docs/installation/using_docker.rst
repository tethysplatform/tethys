.. _using_docker:

************
Using Docker
************


To facilitate leveraging the full capabilities of Tethys Platform, Docker containers are provided to allow the :doc:`../software_suite` to be easily installed. To use these containers you must first install Docker. The Tethys installation script :file:`install_tethys.sh` will support installing the community edition of Docker on several Linux distributions. To install Docker when installing Tethys add the `--install-docker` option. You can also add the `--docker-options` options to pass options to the `tethys docker init` command (see the :ref:`tethys_cli_docker` documentation).

To install Docker on other systems or to install the enterprise edition of Docker please refer to the `Docker installation documentation <https://docs.docker.com/engine/install/>`_

Use the following Tethys command to start the Docker containers.

::

  tethys docker start

You are now ready to link your Tethys Portal with the Docker containers using the web admin interface. Follow the :doc:`./web_admin_setup` tutorial to finish setting up your Tethys Platform.

If you would like to test the Docker containers, see :doc:`../supplementary/docker_testing`.