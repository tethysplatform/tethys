.. _scaffolded_app_recipe :

:orphan:

************
Scaffolded App Recipe
************

Tethys Platform provides an easy way to create new app projects called a scaffold. The scaffold generates a Tethys app project with the minimum files and the folder structure that is required (see :doc:`../../supplementary/app_project`).

.. tip::

   You will need to use the command line/terminal to manage your app and run the development server. See the :doc:`../../supplementary/terminal_quick_guide` article for some tips if you are new to command line.

   Windows Users: Use the Anaconda Powershell Prompt to run Tethys commands.  Visit the Anaconda site for instructions on installing `Anaconda Powershell Prompt <https://docs.anaconda.com/anaconda/install/>`_ or `Miniconda Powershell Prompt <https://docs.anaconda.com/miniconda/miniconda-install/>`_.

1. Generate Scaffold
====================
To generate a new app using the scaffold, open a terminal, press :kbd:`CTRL-C` to stop the development server if it is still running, and execute the following commands:

.. code-block:: bash

    conda activate tethys
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

Use the following commmand to start up the development server:

.. code-block:: bash

    tethys start


Browse to `<http://127.0.0.1:8000/apps/>`_ in a web browser and login with the **default portal user**:

* **username**: admin
* **password**: pass


If all has gone well, you should see your app listed on the app library page. Click on the app tile to launch it. Exploring your new app won't take long, because there is only one page. Familiarize yourself with different parts of the app interface (see below).

.. figure:: ../images/app_controls.png
    :width: 650px

**Parts of a Tethys app interface: (1) app navigation toggle and app branding; (2) exit button, settings, button, and custom buttons; (3) app navigation, (4) app content, and (5) app actions.**

.. tip::

    To stop the development server press :kbd:`CTRL-C`.