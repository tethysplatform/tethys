.. _tethys_cli_docker:

docker command
**************

Manage Tethys-sponsored Docker containers. To learn more about Docker, see `What is Docker? <https://www.docker.com/resources/what-container/>`_.

.. important::

    You must have Docker installed and add your user to the ``docker`` group to use the Tethys ``docker`` command (see: `Install Docker <https://docs.docker.com/get-started/get-docker/>`_ and `Post-installation steps for Linux <https://docs.docker.com/engine/install/linux-postinstall/>`_).

    Additionally, this feature requires the ``docker-py`` library to be installed. Starting with Tethys 5.0 or if you are using ``micro-tethys-platform``, you will need to install ``docker-py`` using conda as follows:

    .. code-block:: bash

        # conda: conda-forge channel strongly recommended
        conda install -c conda-forge docker-py


.. argparse::
   :module: tethys_cli
   :func: tethys_command_parser
   :prog: tethys
   :path: docker