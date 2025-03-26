********************************************************
Part 1 Primer: Google Earth Engine for Tethys Developers
********************************************************

**Last Updated:** July 2024

This tutorial provides links to Google Earth Engine tutorials and resources that can be used to learn what you need to know for this Tethys tutorial. This is by no means exhaustive and we encourage you to familiarize yourself with everything Google Earth Engine has to offer by visiting their documentation: `<https://developers.google.com/earth-engine/>`_. You will need an active `Google Earth Engine account <https://signup.earthengine.google.com>`_ to complete this tutorial.

1. What is Google Earth Engine?
===============================

Review the `Google Earth Engine Introduction <https://developers.google.com/earth-engine/>`_.


2. Google Earth Engine JavaScript API
=====================================

As a Tethys Developer, you will likely use the the Python API more often than the JavaScript API. However, there are not as many examples or documentation for Python. We recommend becoming familiar with the JavaScript examples and then learning how to convert any JavaScript example into the Python equivalent.

Complete the `Get Started guide <https://developers.google.com/earth-engine/guides/getstarted>`_.

3. Google Earth Engine Python API
=================================

Complete the `Python Installation - Colab Notebook guide <https://developers.google.com/earth-engine/guides/python_install-colab.html>`_

4. Convert JavaScript Example to Python
=======================================

1. Review the following syntax differences between the JavaScript and Python APIs: `JavaScript-Python Syntax Comparison <https://developers.google.com/earth-engine/guides/python_install>`_

2. Choose an example from the **Scripts** tab of the `Code Editor <https://code.earthengine.google.com/>`_ and convert it into Python in the Colab editor using the guidelines from the article above.

5. Create a Google Cloud Account and New Project
====================================================
If you plan to use Google Earth Engine in your Tethys App, you will need to create a Google Cloud Account and set up a new project. 
Follow the instructions in the `Google Cloud Platform Quickstart <https://cloud.google.com/resource-manager/docs/creating-managing-projects>`_.

6. Create a Google Earth Engine Conda Environment
=================================================

Create a new Conda environment with Google Earth Engine installed:

.. code-block:: bash

    conda create --name ee
    conda activate ee
    conda install -c conda-forge earthengine-api

.. _authenticate_gee_locally:

7. Authenticate with Google Earth Engine
========================================

Before you can use Google Earth Engine in your Tethys Development or in a Jupyter Notebook, you'll need to do a **one-time** authentication using the command line tool:

.. code-block:: bash

    earthengine authenticate

.. note::

    The Google Earth Engine command line tool is installed when you install the conda package.

A URL will be provided in the terminal. Open the URL in a browser and follow the instructions to authenticate with your Google Earth Engine account.

Next, you'll need to set your project ID for the Google Earth Engine Python API moving forward:

Run the following command and replace ``<project_id>`` with your Google Cloud Project ID:

.. code-block:: bash

    earthengine set_project <project_id>

8. Review GEE Key Concepts
==========================

* `Client vs. Server <https://developers.google.com/earth-engine/guides/client_server>`_
* `Deferred Execution <https://developers.google.com/earth-engine/guides/deferred_execution>`_
* `Scale <https://developers.google.com/earth-engine/guides/scale>`_
* `Projections <https://developers.google.com/earth-engine/guides/projections>`_
* `Debugging <https://developers.google.com/earth-engine/guides/debugging>`_

Reference
=========

* `Earth Engine Code Editor <https://developers.google.com/earth-engine/guides/playground>`_
* `Python Installation <https://developers.google.com/earth-engine/guides/python_install>`_
* `Install into an Existing Conda Installation <https://developers.google.com/earth-engine/guides/python_install-conda.html#install_api>`_
* `Earth Engine Command Line Tool <https://developers.google.com/earth-engine/guides/command_line>`_
* `Updating the Python API <https://developers.google.com/earth-engine/guides/python_install-conda.html#updating_the_api>`_
