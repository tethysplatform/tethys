*******************************
Create a New Tethys App Project
*******************************

**Last Updated:** May 2017

Tethys Platform provides an easy way to create new app projects called a scaffold. The scaffold generates a Tethys app project with the minimum files and the folder structure that is required (see :doc:`../../supplementary/app_project`).

.. tip::

   You will need to use the command line/terminal to manage your app and run the development server. See the :doc:`../../supplementary/terminal_quick_guide` article for some tips if you are new to command line.

Generate Scaffold
=================

To generate a new app using the scaffold, open a terminal, press :kbd:`CTRL-C` to stop the development server if it is still running, and execute the following commands:

::

             $ t
    (tethys) $ mkdir ~/tethysdev
    (tethys) $ cd ~/tethysdev
    (tethys) $ tethys scaffold dam_inventory

You will be prompted to enter metadata about your app such as, proper name, version, author, and description. All of these metadata are optional. You can accept the default value by pressing enter, repeatedly.

The commands you entered did the following tasks:

1. activated the Tethys :term:`Python conda environment`,
2. created a new directory called "tethysdev" in your home directory,
3. changed your working directory into the :file:`tethysdev` directory, and
4. executed the :command:`tethys scaffold` command to create the new app.

In a file browser change into your :file:`Home` directory and open the :file:`tethysdev` directory. If the scaffolding worked, you should see a directory called :file:`tethysapp-dam_inventory`. All of the source code for your app is located in this directory. Open the :file:`tethysapp-dam_inventory` and explore the contents. The main directory of your app project, :file:`dam_inventory`, is located within a namespace directory called :file:`tethysapp`. Each part of the app project will be explained throughout these tutorials. For more information about the app project structure, see :doc:`../../supplementary/app_project`.

Development Installation
========================

Now that you have a new Tethys app project, you need to install the app on your development Tethys Portal. In a terminal, change into the :file:`tethysapp-dam_inventory` directory and execute the :command:`python setup.py develop` command. Be sure to activate the Tethys :term:`Python conda environment` if it is not already activated (see line 1 of the first code block):

::

    (tethys) $ cd ~/tethysdev/tethysapp-dam_inventory
    (tethys) $ python setup.py develop


View Your New App
=================

Use start up the development server:

::

    (tethys) $ tethys manage start

OR use the `tms` alias:

::

    (tethys) $ tms

Browse to `<http://127.0.0.1:8000/apps>`_ in a web browser. If all has gone well, you should see your app listed on the app library page. Exploring your new app won't take long, because there is only one page. Familiarize yourself with different parts of the app interface (see below).

.. figure:: ../../images/app_controls.png
    :width: 650px

**Parts of a Tethys app interface: (1) app navigation toggle, (2) exit button, (3) app navigation, (4) actions, and (5) app content.**

.. tip::

    To stop the development server press :kbd:`CTRL-C`.



App Project Paths
=================

Throughout the tutorial, you will be asked to open various files. Most of the files will be located in your :term:`app package` directory which shares the name of your app: "dam_inventory". If you generated your scaffold exactly as above, this directory will be located at the following path:

::

    # Path to App Package Directory
    ~/tethysdev/tethysapp-dam_inventory/tethysapp/dam_inventory/

For convenience, all paths in the following tutorials will be given relative to the :term:`app package` directory. For example:

::

    # Relative App Package Directory Notation
    dam_inventory/controllers.py

.. tip::

    As you explore the contents of your app project, you will notice that many of the directories have files named :file:`\_\_init\_\_.py`. Though many of these files are empty, they are important and should not be deleted. They inform Python that the containing directory is a Python package. Python packages and their contents can be imported in Python scripts. Removing the :file:`\_\_init\_\_.py` files will result in breaking import statements and it could make some of your code inaccessible. Similarly, if you add a directory to your project that contains Python modules and you would like them to be made available to your code, add a :file:`\_\_init\_\_.py` file to the directory to make it a package.