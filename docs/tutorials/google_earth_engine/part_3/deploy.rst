*******************************
Deploy App to Production Server
*******************************

**Last Updated:** July 2024

In this tutorial you will learn how to install the Google Earth Tethys app in a production environment. If you don't have access to a machine with a production installation of Tethys Platform, we recommend you create a new Virtual Machine and install Tethys on it. Refer to :ref:`production_installation`.

Topics covered in this tutorial include:

* Installing Apps in Production
* Cloning from GitHub

.. figure:: ../../../images/tutorial/gee/deploy_app.png
    :width: 800px
    :align: center

1. Copy Google Earth Engine Key to Server
=========================================

You will need to copy the Google Earth Engine service account key file you created earlier to the server (see: :ref:`service_account_key`). If you have SSH access to the machine, this is most easily done using `scp <https://linux.die.net/man/1/scp>`_:

    .. code-block:: bash

        scp </path/to/local/file> <username>@<server_host>:</path/on/server>

1. We recommended that you ``scp`` the file to the :file:`/tmp` directory and then move it to ``TETHYS_HOME``:

    **System with key file**:

    .. code-block:: bash

        scp </path/to/key.json> <username>@<host>:/tmp/gee_key.json

    **On Server**:

    .. code-block:: bash

        mv </tmp/key.json> ~/.tethys/

2. Change the ownership of the file to the ``NGINX_USER`` and restrict it to read-only access:

    **Ubuntu**:

        .. code-block:: bash

            sudo chown www-data: ~/.tethys/gee_key.json
            sudo chmod 0444 ~/.tethys/gee_key.json



    **CentOS**:

        .. code-block:: bash

            sudo chown nginx: ~/.tethys/gee_key.json
            sudo chmod 0444 ~/.tethys/gee_key.json

2. Follow App Installation Guide
================================

Use the :ref:`installing_apps_production` guide to install the Earth Engine app on the server with the following clarifications:

* **Download App Source Code**: Clone the GitHub repository you setup in the :ref:`publish_app_to_github` tutorial.
* **Install App**: You will be prompted to set values for the ``service_account_email`` and ``private_key_file`` app settings. You may skip entering the values now and set them via the app settings page later.
* **Configure Additional App Settings**: Navigate to the app settings admin page for the Earth Engine app and verify that the ``service_account_email`` and ``private_key_file`` settings are configured correctly.
* **Initialize Persistent Stores**: This step is not required for the Earth Engine app.

3. Verify
=========

Navigate to ``http(s)://<HOST_OF_SERVER>/apps/earth-engine/viewer/`` and verify the following:

1. Load several datasets and ensure the imagery is displayed on the map.
2. Test the Plot Area of Interest capability.
3. Upload a boundary shapefile and verify that the imagery is clipped to the extents of that boundary.

Troubleshooting
===============

* If you encounter a 500 error while accessing the Viewer page check the app settings and verify that ``service_account_email`` and ``private_key_file`` are set correctly.
* Verify that the service account has been registered to use the Google Earth Engine API.
* Check the Tethys log for errors: :file:`/var/log/tethys/tethys.log`