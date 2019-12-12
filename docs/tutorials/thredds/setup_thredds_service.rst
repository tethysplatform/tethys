*********************
Setup THREDDS Service
*********************

**Last Updated:** December 2019

In this tutorial we will learn how to start a THREDDS server using the Docker container that is included with Tethys Platform. We'll also register the THREDDS server as a Tethys Service so can more easily use it in the app. The following topics will be covered in this tutorial:

* Tethys Docker Containers
* Tethys Services
* Tethys Service App Settings

0. Start From Previous Solution (Optional)
==========================================

If you wish to use the previous solution as a starting point:

.. parsed-literal::

    git clone https://github.com/tethysplatform/tethysapp-thredds_tutorial.git
    cd tethysapp-thredds_tutorial
    git checkout -b new-app-project-solution new-app-project-solution-|version|


1. Create a Spatial Dataset Service App Setting
===============================================

Add the following method to your :term:`app class` to define a new spatial dataset services setting for your app:

.. code-block:: python

    from tethys_sdk.app_settings import SpatialDatasetServiceSetting

    class ThreddsTutorial(TethysAppBase):
        ...

        def spatial_dataset_service_settings(self):
            """
            Example spatial_dataset_service_settings method.
            """
            sds_settings = (
                SpatialDatasetServiceSetting(
                    name='thredds_service',
                    description='THREDDS service for app to use',
                    engine=SpatialDatasetServiceSetting.THREDDS,
                    required=True,
                ),
            )

            return sds_settings



2. Start the THREDDS Docker
===========================

1. Initialize the THREDDS Docker container:

.. code-block:: bash

    tethys docker init -c thredds

.. note::

    The command ``tethys docker init`` only needs to be run the first time you are creating a container. If it already exists, you can skip to the next step.


2. Start the THREDDS Docker container:

.. code-block:: bash

    tethys docker start -c thredds

.. tip::

    To stop the docker container:

    .. code-block:: bash

        tethys docker stop -c thredds

    For more information about the Docker interface in Tethys Platform see the :ref:`tethys_cli_docker` reference.

3. Obtain the endpoint for the THREDDS Docker container:

.. code-block:: bash

    tethys docker ip

.. todo::

    Alternatively, you may use an existing THREDDS server for this tutorial.


3. Add Tutorial Data to THREDDS
===============================

.. todo::

    Add tutorial data to THREDDS


4. Create THREDDS Spatial Dataset Service
=========================================

1. Exit the app and navigate to the **Site Administration** page by selecting ``Site Admin`` from the drop down menu located to the right of your user name.

2. Scroll down to the **TETHYS SERVICES** section of the page.

3. Click on the ``Spatial Dataset Services`` link.

4. Click on the ``ADD SPATIAL DATASET SERVICE`` button to create a new Spatial Dataset Service.

5. Enter the following information for the new Spatial Dataset Service:

    * Name: primary_thredds
    * Engine: THREDDS
    * Endpoint: <endpoint from step 2.3>
    * Public Endpoint: <endpoint from step 2.3>
    * ApiKey: (LEAVE BLANK)
    * Username: admin
    * Password: <password you defined in step 2.1>

    .. important::

         For the purposes of this tutorial, the Public Endpoint is the same as the (internal) Endpoint. However, in a production deployment of Tethys Platform, **the Public Endpoint needs to be the publicly accessible address** of the THREDDS server.

6. Press the ``Save`` button to save the new Spatial Dataset Service.

.. todo:

    * Add screen capture of the filled out new sds form.

5. Assign THREDDS Service to App Setting
========================================

1. Navigate back to the **Site Administration** page (see step 4.1).

2. Scroll down to the **TETHYS APPS** section of the page.

3. Click on the ``Installed Apps`` link.

4. Click on the ``THREDDS Tutorial`` link.

5. Scroll down to the **SPATIAL DATASET SERVICE SETTINGS** section.

6. Select the ``primary_thredds`` as the spatial dataset service for the ``thredds_service`` app setting.


6. Solution
===========

This concludes the New App Project portion of the THREDDS Tutorial. You can view the solution on GitHub at `<https://github.com/tethysplatform/tethysapp-thredds_tutorial/tree/thredds-service-solution-3.0>`_ or clone it as follows:

.. parsed-literal::

    git clone https://github.com/tethysplatform/tethysapp-thredds_tutorial.git
    cd tethysapp-thredds_tutorial
    git checkout -b thredds-service-solution thredds-service-solution-|version|