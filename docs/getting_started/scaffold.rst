*******************************
Create a New Tethys App Project
*******************************

**Last Updated:** November 17, 2014

Tethys Platform provides an easy way to create new app projects called a scaffold. The scaffold generates a Tethys app project with the minimum files and the folder structure that is required (see :doc:`../supplementary/app_project`). In this tutorial you start a new Tethys app project using the scaffold and you will install the app into your Tethys Platform ready for development.

.. tip::

   You will need to use the command line/terminal to manage your app and run the development server. See the :doc:`../supplementary/terminal_quick_guide` article for some tips if you are new to command line.

Generate Scaffold
=================

To generate a new app using the scaffold, open a terminal, press :kbd:`CTRL-C` to stop the development server if it is still running, and execute the following commands:

::

    $ . /usr/lib/tethys/bin/activate
    $ mkdir ~/tethysdev
    $ cd ~/tethysdev
    $ tethys scaffold my_first_app

You will be prompted to enter metadata about your app such as, proper name, version, author, and description. All of these are optional and you can skip an item by pressing enter.

The commands you entered did the following tasks:

1. activated the Tethys :term:`Python virtual environment`,
2. created a new directory called "tethysdev" in your home directory,
3. changed your working directory into the :file:`tethysdev` directory, and
4. executed the :command:`tethys scaffold` command to create the new app.

In a file browser change into your :file:`Home` directory and open the :file:`tethysdev` directory. If the scaffolding worked, you should see a directory called :file:`tethysapp-my_first_app`. All of the source code for your app will be stored in this directory. Open the :file:`tethysapp-my_first_app` and explore the contents. The main directory of your app project, :file:`my_first_app`, is located within a namespace directory called :file:`tethysapp`. Each part of the app project will be explained throughout these tutorials. For more information about the app project structure, see :doc:`../supplementary/app_project`.

Development Installation
========================

Now that you have a new Tethys app project, you need to install the app into Tethys Platform. In a terminal, change into the :file:`tethysapp-my_first_app` directory and execute the :command:`python setup.py develop` command. Be sure to activate the Tethys :term:`Python virtual environment` if it is not already activated (see line 1 of the first code block):

::

    $ cd ~/tethysdev/tethysapp-my_first_app
    $ python setup.py develop


View Your New App
=================

Use the :command:`tethys manage start` command to start up the development server:

::

    $ tethys manage start

Browse to `<http://127.0.0.1:8000/apps>`_. If all has gone well, you should see your app listed on the app library page. Exploring your new app won't take long, because there is only one page. Familiarize yourself with different parts of the app interface (see below).

.. figure:: ../images/app_controls.png
    :width: 650px

    Parts of a Tethys app interface: (1) app navigation toggle, (2) exit button, (3) app navigation, (4) actions, and (5) app content.

.. tip::

    To stop the development server press :kbd:`CTRL-C`.

Model View Controller
=====================

Tethys apps are developed using the :term:`Model View Controller` (MVC) development pattern. Following the MVC pattern will make your app project easier to develop and manage in the future. Most of the code in your app will fall into one of the three MVC categories. The Model represents the data of your app, the View is composed of the representation of the data, and the Controller consists of the logic to prepare the data for the view and any other logic your app needs. In the next few tutorials, you will be introduced to how the MVC development paradigm is used to develop Tethys apps. For more information about MVC, see :doc:`../supplementary/key_concepts`.

App Project Paths
=================

Throughout the tutorial, you will be asked to open various files. Most of the files will be located in your :term:`app package` directory which shares the name of your app: "my_first_app". If you generated your scaffold exactly as above, this directory will be located at the following path:

::

    # Path to App Package Directory
    ~/tethysdev/tethysapp-my_first_app/tethysapp/my_first_app/

For convenience, all paths in the following tutorials will be given relative to the :term:`app package` directory. For example:

::

    # Relative App Package Directory Notation
    my_first_app/controllers.py

As you explore the contents of your app project, you will notice that many of the directories have filed named "__init__.py". Though many of these files are empty, they are important and should not be deleted. They tell Python that this directory is a Python package. Python packages and their contents can be imported in Python scripts. Removing the :file:`\_\_init\_\_.py` files could result in breaking import statements and it could make some of your code inaccessible. Similarly, if you add a directory to your project that contains Python modules you would like to be made available to your code, add a :file:`\_\_init\_\_.py` file to the directory to make it a package.