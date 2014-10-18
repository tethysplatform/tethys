********************************
Working with CKAN in Development
********************************

**Last Updated:** May 29, 2014

Running CKAN
============

While you are developing apps, you will use the Paste server to run CKAN. Before you start up the server, make sure that Jetty and PostgreSQL servers are running:

::

    $ sudo service postgresql start
    $ sudo service jetty start

.. note:: If you installed Solr using Tomcat instead of Jetty, change the second :command:`start` command to :command:`tomcat6` instead of :command:`jetty`.

Next, activate your CKAN Python virtual environment and execute the :command:`paster serve` command. You will know that your virtual environment is activated, beacuse the name of it will appear in parenthesis next to your terminal cursor. We recommned using the option :command:`--reload` when you are developing. This will cause the server to restart anytime you save changes in a file while developing your app. In a terminal:

::

    $ . /usr/lib/ckan/default/bin/activate
    $  paster serve --reload /etc/ckan/default/development.ini

Open a web browser enter the following URL to see CKAN:

::

    http://localhost:5000

.. tip::

    You can stop the paster server using the keyboard shortcut :kbd:`ctrl-C` in the terminal. Then run the ``paster serve`` command from above to start it up again.

Debugging in CKAN
=================

To enable debugging in CKAN, open the configuration file (:file:`/etc/ckan/default/development.ini`) and change the **debug** parameter to *true* and restart the paster server.

::

    debug = true

If you get an error that says something to the effect of "cannot find main.debug.css" then do the following:

::

    $ cp /usr/lib/ckan/default/src/ckan/ckan/public/base/css/main.debug.min.css /usr/lib/ckan/default/src/ckan/ckan/public/base/css/main.debug.css

Restart the paster server and the problem should be resolved.

.. caution::

    These instructions do not apply when using the Docker development method.
