.. _tethys_cli_docker:

docker command
**************

Manage Tethys-sponsored Docker containers. To learn more about Docker, see `What is Docker? <https://www.docker.com/whatisdocker/>`_.

.. important::

    You must have Docker installed and add your user to the ``docker`` group to use the Tethys ``docker`` command (see: `Install Docker <https://docs.docker.com/install/>`_ and `Post-installation steps for Linux <https://docs.docker.com/install/linux/linux-postinstall/>`_).

.. argparse::
   :module: tethys_cli
   :func: tethys_command_parser
   :prog: tethys
   :path: docker