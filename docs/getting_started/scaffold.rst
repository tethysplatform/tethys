******************************
Generate New App with Scaffold
******************************

**Last Updated:** May 20, 2014

The Tethys Apps plugin provides a scaffold for generating new apps projects. The scaffold generates a very simple app project with all of the major components and the structure discussed in :doc:`../app_project`. This portion of the tutorial will describe how to start a new app project using the scaffold and configure it to run as a Tethys App in CKAN.

Generate Scaffold
=================

To generate a new app scaffold, open a terminal and activate your CKAN virtual environment. Create a new directory in your home directory called :file:`tethysdev` and path into this directory. Finally, execute the :command:`paster create` command:

::

    $ . /usr/lib/ckan/default/bin/activate
    $ mkdir ~/tethysdev
    $ cd ~/tethysdev
    $ paster create -t ckanapp ckanapp-my_first_app

Follow the interactive prompts to create metadata for you new app (the only required parameter is the proper name). The :command:`paster create` command generates a new Tethys App project using a template called *ckanapp* that ships with the Tethys Apps plugin. In a file browser open the :file:`ckanapp-my_first_app` directory and familiarize yourself with its contents. Notice that the files are organized in the same manner as described in :doc:`../app_project`.

Development Installation
========================

Next, install the app into the CKAN Python environment. This will also install any dependencies of your app listed in the :term:`setup script` (:file:`setup.py`). Rather than running the :command:`install` command on the :term:`setup script`, run the :command:`develop` command instead. This makes it so you don't have to reinstall the app everytime you make a change to the source code. Be sure to activate the CKAN Python virtual environment if it is not already activated. In a terminal run:

::

    $ . /usr/lib/ckan/default/bin/activate
    $ cd ~/tethysdev/ckanapp-my_first_app
    $ python setup.py develop


Start up the Paste server and browse to your local CKAN site. If all has gone well, you should see your app listed on the app library page. Exploring your new app doesn't take long, because there is only one page and it will be empty. In the next few tutorials, we'll introduce how the Model View Controller (MVC) development paradigm is used to develop apps.

.. note::

    If the Paste server is running when you create the app, you will need to restart it. Stop the server by pressing :kbd:`CTRL-C` and start the server again by executing the :command:`paster serve` command. A shortcut to finding this command is to press the up arrow.
