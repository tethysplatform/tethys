*******************************
Create a New Tethys App Project
*******************************

**Last Updated:** November 11, 2014

Tethys Platform provides a scaffold for generating new app projects. The scaffold generates a Tethys app project with
the minimum files and the file structure that is required (see :doc:`../app_project`). This section of the tutorial will
describe how to start a new Tethys app project using the scaffold and it will describe how to install the app into your
Tethys platform for development.

Generate Scaffold
=================

To generate a new app scaffold, open a terminal and activate the Tethys virtual environment. Create a new directory in
your home directory called :file:`tethysdev` and change into this directory. Finally, execute the
:command:`tethys scaffold` command, giving it the name of the new app project. App project names must contain only
letters, numbers, and underscores (_). Follow the interactive prompts to create
metadata for you new app.:

::

    $ . /usr/lib/tethys/bin/activate
    $ mkdir ~/tethysdev
    $ cd ~/tethysdev
    $ tethys scaffold my_first_app

In a file browser open the :file:`tethysapp-my_first_app` directory and familiarize yourself with its contents. The
scaffold automatically prefixes your app project directory name with "tethysapp-". The main package of your app project,
"my_first_app", is located within a namespace package called "tethysapp". For more information about the app project
structure, see :doc:`../app_project`.

Development Installation
========================

Next you will use the :term:`setup script` (:file:`setup.py`) to install the app into Tethys Platform. This will also
install any Python dependencies of your app. In a terminal, change into the :file:`tethysapp-my_first_app` and execute
the :command:`python setup.py develop` command. Be sure to activate the Tethys :term:`Python virtual environment` if
it is not already activated:

::

    $ . /usr/lib/tethys/bin/activate
    $ cd ~/tethysdev/tethysapp-my_first_app
    $ python setup.py develop


View Your New App
=================

Use the :command:`tethys manage start` command to start up the development server and browse to
`<http://127.0.0.1:8000/apps>`_.

::

    $ tethys manage start

If all has gone well, you should see your app listed on the app library page. Exploring your new app won't take long,
because there is only one page. Familiarize yourself with different parts of the app interface (see Figure 1).

.. figure:: ../images/app_controls.png
    :width: 650px

    **Figure 1.** Tethys app interface: (1) app navigation toggle, (2) exit button, (3) app navigation, (4) actions, and (5) app content.

In the next few tutorials, we'll introduce how the Model View Controller (MVC) development paradigm that is used to
develop Tethys apps.

.. tip::

    To stop the development server press :kbd:`CTRL-C`.
