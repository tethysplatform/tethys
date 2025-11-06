.. _scaffold_an_app_via_command_line :



********************************************
Scaffold and Install an App via Command Line
********************************************

Tethys Platform provides an easy way to create new app projects via command line with the ``scaffold`` command. This command generates a Tethys app project with the minimum files and the folder structure that is required (see :doc:`../../supplementary/app_project`).

**Last Updated:** October 2025

.. tip::

   You will need to use the command line/terminal to manage your app and run the development server. See the :doc:`../../supplementary/terminal_quick_guide` article for some tips if you are new to command line.

   Windows Users: Use the Anaconda Powershell Prompt to run Tethys commands.  Visit the Anaconda site for instructions on installing `Anaconda Powershell Prompt <https://docs.anaconda.com/anaconda/install/>`_ or `Miniconda Powershell Prompt <https://docs.anaconda.com/miniconda/miniconda-install/>`_.

.. note::

    See :ref:`scaffold_an_app_via_the_portal` if you would rather avoid using the command line.

1. Generate Scaffold
=====================
To generate a new app using the ``scaffold`` command, open a terminal, :ref:`activate_environment`, and execute the following commands:

.. code-block:: bash

    tethys scaffold new_app   

You will be prompted to enter metadata about your app such as, proper name, version, author, and description. All of these metadata are optional. You can accept the default value that is shown in the square brackets by pressing enter.

In a file browser change into your home directory and open the :file:`tethysdev` directory. If the scaffolding worked, you should see a directory called :file:`tethysapp-new_app`. All of the source code for your app is located in this directory. For more information about the app project structure, see :doc:`../../supplementary/app_project`.

2. Development Installation
===========================

Now that you have a new Tethys app project, you need to install the app on your development Tethys Portal. In a terminal, change into the :file:`tethysapp-new_app` directory and execute the :command:`tethys install -d` command:

.. code-block:: bash

    cd tethysapp-new_app
    tethys install -d

.. tip::

    Windows Users: If you get an error when running ``tethys install -d``, then you have insufficient permissions to install your app in development mode. Either try opening the ``tethys_cmd.bat`` as an administrator and run the commands again, or run ``tethys install``. The disadvantage to this method is that each time you want Tethys to reflect changes to your app code, you will need to run ``tethys install`` again.

3. View Your New App
====================

.. include:: steps/start_tethys_step.rst

.. figure:: ../../docs/images/recipes/scaffold_pic.png
    :width: 800px
    :align: center    
