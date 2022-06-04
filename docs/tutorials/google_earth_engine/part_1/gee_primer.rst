********************************************************
Part 1 Primer: Google Earth Engine for Tethys Developers
********************************************************

**Last Updated:** June 2022

This tutorial provides links to Google Earth Engine tutorials and resources that can be used to learn what you need to know for this Tethys tutorial. This is by no means exhaustive and we encourage you familiarize yourself with everything Google Earth Engine has to offer by visiting their documentation: `<https://developers.google.com/earth-engine/>`_. You will need an active `Google Earth Engine account <https://signup.earthengine.google.com>`_ to complete this tutorial.

1. What is Google Earth Engine?
===============================

Review the `Google Earth Engine Introduction <https://developers.google.com/earth-engine/>`_.


2. Google Earth Engine JavaScript API
=====================================

As a Tethys Developer, you will likely use the the Python API more often than the JavaScript API. However, there are not as many examples or documentation for Python. We recommend becoming familiar with the JavaScript examples and then learning how to convert any JavaScript example into the Python equivalent.

Complete the `Get Started guide <https://developers.google.com/earth-engine/getstarted>`_.

3. Google Earth Engine Python API
=================================

Complete the `Python Installation - Colab Notebook guide <https://developers.google.com/earth-engine/python_install-colab.html>`_

4. Convert JavaScript Example to Python
=======================================

1. Review the following syntax differences between the JavaScript and Python APIs: `JavaScript-Python Syntax Comparison <https://developers.google.com/earth-engine/python_install>`_

2. Choose an example from the **Scripts** tab of the `Code Editor <https://code.earthengine.google.com/>`_ and convert it into Python in the Colab editor using the guidelines from the article above.

5. Create a Google Earth Engine Conda Environment
=================================================

Create a new Conda environment with Google Earth Engine installed:

.. code-block:: bash

    conda create --name ee
    conda activate ee
    conda install -c conda-forge earthengine-api

.. _authenticate_gee_locally:

6. Authenticate with Google Earth Engine
========================================

Before you can use Google Earth Engine in your Tethys Development or in a Jupyter Notebook, you'll need to do a **one-time** authentication using the command line tool:

.. code-block:: bash

    earthengine authenticate

.. note::

    The Google Earth Engine command line tool is installed when you install the conda package.

A URL will be provided that generates an authorization code upon agreement. Copy the authorization code and enter it as command line input. This will save a token to a credentials file in the following location:

.. code-block:: bash

    ls $HOME/.config/earthengine/credentials

7. Review GEE Key Concepts
==========================

* `Client vs. Server <https://developers.google.com/earth-engine/client_server>`_
* `Deferred Execution <https://developers.google.com/earth-engine/deferred_execution>`_
* `Scale <https://developers.google.com/earth-engine/scale>`_
* `Projections <https://developers.google.com/earth-engine/projections>`_
* `Debugging <https://developers.google.com/earth-engine/debugging>`_

Reference
=========

* `Earth Engine Code Editor <https://developers.google.com/earth-engine/playground>`_
* `Python Installation <https://developers.google.com/earth-engine/python_install>`_
* `Install into an Existing Conda Installation <https://developers.google.com/earth-engine/python_install-conda.html#install_api>`_
* `Earth Engine Command Line Tool <https://developers.google.com/earth-engine/command_line>`_
* `Updating the Python API <https://developers.google.com/earth-engine/python_install-conda.html#updating_the_api>`_
