*********************************
CKAN Installation Troubleshooting
*********************************

**Last Updated:** November 17, 2014

A recent change to the ``libtomcat6-java`` library has caused some issues with Solr running through Jetty. If you encounter these issues (i.e.: some error about a tomcat library), Solr can be configured to run through Tomcat instead. To use Tomcat instead of Jetty, execute the following commands:

::

    $ sudo apt-get remove solr-jetty
    $ sudo apt-get install solr-tomcat

Next, open the tomcat configuration file (/etc/tomcat6) and change the port attribute of the Connector to **8983**. Start tomcat like so:

::

    $ sudo service tomcat6 start

If you get an error like *Permission denied:'/var/lib/ckan/default/storage'* run the following commands:

::

    $ sudo chown -R `whoami` /var/lib/ckan/default
    $ sudo chmod -R u+rwx /var/lib/ckan/default