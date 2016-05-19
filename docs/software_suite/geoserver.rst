****************
GeoServer Docker
****************

**Last Updated:** May 18, 2016

Installation
============

This is how you install the new GeoServer Docker...

Migrate to New GeoServer Docker
===============================

Use these instructions to migrate the data in a GeoServer 2.7.0 Docker to a newer version. You can see the version of GeoServer is displayed on the main admin page of GeoServer.

1. Extract data from GeoServer docker (the container that Tethys creates for GeoServer is named tethys_geoserver)

  ::

      $ mkdir ~/backup
      $ cd ~/backup
      $ docker run --rm --volumes-from tethys_geoserver -v $(pwd):/backup ubuntu:14.04 tar cvf /backup/backup.tar /var/lib/geoserver/data

2. Rename old GeoServer docker container as a backup and verify that it was renamed

  ::

      $ docker rename tethys_geoserver tethys_geoserver_bak
      $ docker ps -a

3. Pull new docker container (must have upgraded to Tethys Platform version 1.4.0, which is on dev)

  ::

      $ . /usr/lib/tethys/bin/activate
      (tethys) $ tethys docker init

4. Respond to the prompts to configure the new GeoServer container, which can be configured to run in a clustered mode. Here is a short explanation of each of the parameters:

    * GeoServer Instances Enabled: This is the number of parallel running GeoServer's to start up when the docker starts. All of the GeoServer instances share the same directory and remain synced via the JMS clustering extension (see: http://docs.geoserver.org/2.8.x/en/user/community/jms-cluster/installation.html). Access to the instances is automatically load balanced via NGINX. The load-balanced cluster of GeoServers is accessed using port 8181 and this should be used as the endpoint for you GeoServer docker. You will notice that the identifier of the node appears in the top left corner of the GeoServer admin page. When accessing the admin page of the cluster using port 8181, you will always be redirected to the first node. Any changes to this node will be synced to the other nodes, so usually it will be sufficient to administer the GeoServer this way. However, you can access the admin pages of each node directly using ports 8081-8084, respectively, for troubleshooting.
    * GeoServer Instances with REST Enabled: The number of running GeoServer instances that have the REST API enabled. Tethys Dataset Services uses the rest API to manage data (create, read, update, delete) in GeoServer. It is a good idea to leave a few of your GeoServer nodes as read-only (REST disabled) to retain access to GeoServer data even when it is processing data. To configure it this way, be sure this number is less than the number of enabled GeoServer nodes.
    * Control Flow Options: The control flow extenion allows you to limit the number of requests that are allowed to run simultaneously, placing any excess requests into a queue to be executed late. This prevents your GeoServer from becoming overwhelmed during heavy traffic periods.

        There are two ways to configure control flow during setup:
            (1) Automatically derive flow control options based on the number of cores of your computer (recommended for development or inexperienced developers)
            (2) Explicitly set several of the most useful options (useful for a production installation and more experienced developers)

        Note: if you bind the geoserver data directory to the host machine (recommended), you can edit these options by editing the controlflow.properties. Refer to the Control Flow documentation for more details (http://docs.geoserver.org/2.8.x/en/user/extensions/controlflow/index.html).
    * Max timeout: The amount of time in seconds to wait before terminating a request.
    * Min and Max Memory: The amount of memory to allocate as heap space for each GeoServer instance. It is usually a good idea to set the min to be the same as the max to avoid the overhead of allocating additional memory if it is needed. 2 GB per instance is probably the maximum you will need for this and the default of 1 GB is likely to be sufficient for many installations.
        Warning: BE CAREFUL WITH THIS. If you set the min memory to be 2 GB per instance and 4 instances enabled, GeoServer will try to allocate 8GB of memory. If your machine doesn't have 8GB of memory, it will get overwhelmed and lock down.
    * Bind the GeoServer data directory to the Host (HIGHLY RECOMMENDED): This allows you to mount one of the directories on your machine into the docker container. Long story short, this will give you direct access to the GeoServer data directory outside of the docker container. This is useful if you want to configure your controlflow.properties, add data directly to the data directory, or view the files that were uploaded for debugging. The GeoServer docker container will automatically add the demo data to this directory after starting up the first time.
        Note: If the directory that you are binding to doesn't exist or you don't have permission to write to it, the setup operation may fail. To be safe you will want to make the directory before hand and ensure you can write to it.

5. After the new GeoServer installs, start it up and visit the admin page (http://localhost:8181/geoserver) to make sure it is working properly. This also adds the data from the GeoServer to the data directory on the host, so DON'T SKIP THIS STEP. When you are done stop the GeoServer docker.

  ::

      (tethys) $ tethys docker start -c geoserver
      (tethys) $ tethys docker stop -c geoserver

6. Browse to the directory where you bound the GeoServer data directory (default is /usr/lib/tethys/geoserver):

  ::

      $ cd /usr/lib/tethys/geoserver
      $ ls -alh data/

7. You should see the contents of the data directory for the GeoServer docker container. Notice that everything is owned by root. This is because the container runs with the root user. To restore the data from your old container, you will need to delete the contents of this directory and copy over the the data in the tar file in ~/backup.

  ::

      $ sudo rm -rf data/
      $ cp ~/backup/backup.tar .
      $ tar xvf backup.tar --strip 3
      $ rm backup.tar

8. Listing the contents of data again, you should see the data restored from your previous GeoServer docker:

  ::

      $ ls -alh data/

9. Start up the GeoServer container again.

  ::

      (tethys) $ tethys docker start -c geoserver

10. The layer preview and some other features of GeoServer will not work properly until you set the Proxy Base URL due to the clustered configuration of the GeoServer. Navigate to `Settings > Global` and locate the Proxy Base URL field and enter the external URL of your GeoServer (e.g.: http://localhost:8181/geoserver).


  .. note:: Logging in as admin: sometimes it doesn't work the first time (or second, third or forth for that matter). Try, try again until it works.


11. Once you are confident that the data has been successfully migrated from the old GeoServer container to the new one, you should delete the old GeoServer container:

  ::

      $ docker rm tethys_geoserver_bak
