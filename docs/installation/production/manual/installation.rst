.. _production_install_tethys:

***********************
Install Tethys Platform
***********************

**Last Updated:** September 2022

This article will provide an overview of how to install Tethys Portal in a production setup ready to host apps. Currently production installation of Tethys is only supported on Linux. Some parts of these instructions are optimized for Ubuntu, though installation on other Linux distributions will be similar.

Install Miniconda
=================

    1. As of version 3.0, Tethys Platform can be installed using `conda <https://docs.conda.io/projects/conda/en/latest/user-guide/install/>`_. We recommend installing `Miniconda <https://docs.conda.io/en/latest/miniconda.html>`_ as it provides a minimal installation of conda that is appropriate for servers:

        .. code-block:: bash

            cd /tmp
            wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
            bash ./Miniconda3-latest-Linux-x86_64.sh

    2. Read the license and accept when prompted. Install to the default location (:file:`~/miniconda3`) and configure the shell to start on startup.

Install Tethys Platform
=======================

    1. Create a new conda environment called ``tethys`` with the ``tethys-platform`` package installed:

        .. code-block:: bash

            conda create -n tethys -c conda-forge -c tethysplatform tethys-platform

    2. Activate the ``tethys`` conda environment after it is created:

        .. code-block:: bash

            conda activate tethys
