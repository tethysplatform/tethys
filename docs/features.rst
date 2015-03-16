********
Features
********

**Last Updated:** February 2, 2015

Tethys is a platform that can be used to develop and host water resources web applications or web apps. It includes a suite of free and open source software (FOSS) that has been carefully selected to address the unique development needs of water resources web apps. Tethys web apps are developed using a Python software development kit (SDK) which includes programmatic links to each software component. Tethys Platform is powered by the `Django <https://www.djangoproject.com/>`_ Python web framework giving it a solid web foundation with excellent security and performance.

.. figure:: images/features/tethys_platform_diagram.jpg
    :width: 600px
    :align: center

    Tethys Platform include software to meet water resources web app development needs.


Develop Web Apps
================

Tethys Platform is focused on making development of engaging, interactive web apps for water resources as easy as possible. It is backed by free and open source software to address the spatial data, visualization, and computational needs of water resources web apps.

.. figure:: images/features/example_app_page.png
    :width: 600px
    :align: center

    Tethys platform can be used to create engaging, interactive web apps for water resources.


Python Software Development Kit
===============================

Tethys web apps are developed with the `Python programming language <https://www.python.org/>`_ and the Tethys Software Development Kit (SDK). Tethys web apps projects are organized using a Model View Controller (MVC) approach. The SDK provides Python module links to each software component of the Tethys Platform, making the functionality of each software easy to incorporate each in your web apps. In addition, you can use all of the Python modules that you are accustomed to using in your scientific Python scripts to power your web apps.

.. figure:: images/features/app_code.png
    :width: 600px
    :align: center

    Tethys web apps are developed using Python and the Tethys SDK.

.. note::

    Read more about the Tethys SDK by reading the :doc:`./tethys_sdk` documentation.

Templating and Gizmos
=====================

Tethys SDK takes advantage of the Django template system so you can build dynamic pages for your web app while writing less HTML. It also provides a series of modular user interface elements called Gizmos. With only a few lines of code you can add range sliders, toggle switches, auto completes, interactive maps, and dynamic plots to your web app.

.. figure:: images/features/example_gizmo.png
    :width: 600px
    :align: center

    Insert common user interface elements like date pickers, maps, and plots with minimal coding.

.. note::

    Read more about templating and Gizmo by reading the :doc:`./tethys_sdk/templating` and the :doc:`./tethys_sdk/gizmos` documentation.

Developer Tools
===============

Tethys provides a Developer Tools page that is accessible when you run Tethys in developer mode. Developer Tools contain documentation, code examples, and live demos of the features of various features of Tethys. Use it to learn how to add a map or a plot to your web app using Gizmos, browse the available geoprocessing capabilities and formulate geoprocessing requests interactively, and browse the data that is available to web apps via the dataset connections.

.. figure:: images/features/developer_tools.png
    :width: 600px
    :align: center

    Use the Developer Tools page to assist you in development.

Spatial Data
============

Tethys Platform is especially equipped to handle the spatial data needs of your water resources web apps. Included in the software suite is `PostgreSQL <http://www.postgresql.org/>`_ with the `PostGIS <http://postgis.net/>`_ extension for spatial database storage, `GeoServer <http://geoserver.org/>`_ for spatial data publishing, and `52 North WPS <http://52north.org/communities/geoprocessing/wps/>`_ for geoprocessing. Tethys also provides Gizmos for inserting `Google Maps <https://developers.google.com/maps/web/>`_, `Google Earth <https://developers.google.com/earth/>`_, and `OpenLayers <http://openlayers.org/>`_ for interactive spatial data visualizations in your web apps.

.. figure:: images/features/geoprocessing.png
    :width: 500px
    :align: center

    Tethys Platform includes GIS software to meet the spatial needs of web apps.

.. note::

    Refer to the following documentation for more information about the spatial functionality of Tethys: :doc:`./tethys_sdk/persistent_store`,  :doc:`./tethys_sdk/spatial_persistent_store`, :doc:`./tethys_sdk/spatial_publishing`, :doc:`./tethys_sdk/geoprocessing`, and :doc:`./tethys_sdk/visualizing`.

Data Store
==========

Tethys provides mechanisms for plugging into dataset services like CKAN and HydroShare as a means of dataset and file storage.

.. figure:: images/features/datastore.png
    :width: 500px
    :align: center

    Plug into dataset services like CKAN and HydroShare for file datasets.

.. note::

    To learn more, read the :doc:`./tethys_sdk/dataset_services`.

Computing
=========

Tethys includes Python modules that will allow you to provision and run computing jobs in distributed computing environments.

.. figure:: images/features/computing.png
    :width: 500px
    :align: center

    Run the computing jobs of Tethys web app using distributed computing.

With CondorPy you can define your computing jobs and submit them to distributed computing environments provided by `HTCondor <http://research.cs.wisc.edu/htcondor/>`_.

.. figure:: images/features/computing_condorpy.png
    :width: 400px
    :align: center

    CondorPy enables computing jobs to be created and submitted to a HTCondor computing pool.

HTCondor provides a way to make use of the idle computing power that is already available in your office. Alternatively, TethysCluster enables you to provision scalable computing resources in the cloud using commercial services like `Amazon AWS <https://aws.amazon.com/free/cloud-computing-free-tier/?sc_channel=PS&sc_campaign=AWS_Free_Tier_2013_T&sc_country=US&sc_publisher=Google&sc_medium=b_test_cloud_computing_e-amazon_computing&sc_content=50999158962&sc_detail=Amazon%20computing&sc_category=aws_cloud_computing&sc_segment=cloud_computing&sc_matchtype=e&s_kwcid=AL!4422!3!50999158962!e!!g!!amazon%20computing&ef_id=U2k10QAAAbgQyF5m:20141124202406:s>`_ and `Microsoft Azure <https://azure.microsoft.com/en-us/>`_.

.. figure:: images/features/computing_tethyscluster.png
    :width: 600px
    :align: center

    TethysCluster makes it easy to scale your computing resources using commercial cloud services.

Computing resources can be managed in Tethys through the Admin Portal. With just a few clicks new computing clusters can be provisioned and scaled to meet the demands of your current workload.

.. figure:: images/features/computing_admin_portal.png
    :width: 600px
    :align: center

    The Admin Portal provides an easy-to-use interface for provisioning cloud computing resources.

.. note::

    To learn more, read the :doc:`./tethys_sdk/cloud_computing`.

Production Ready
================

After you have a working web app, Tethys Platform can be configured so that it can host your web apps in a production environment. Users and clients will be able to access your web apps via a modern web portal called Tethys Portal. As a Django project, the Tethys Portal is secure and customizable. It also provides a user management system for controlling which users are able to access the web apps.

Apps Library
------------

Apps are easily accessible via the apps library provided by Tethys Portal.

.. figure:: images/features/apps_library.png
    :width: 600px
    :align: center

    Browse available web apps using the Apps Library.


User Management
---------------

The user management system in Tethys allows site administrators the ability to control who has access to which web apps. In addition, users are able to maintain their profiles and control their accounts. Profile pictures are provided by the Gravitar service, so that you don't need to worry about storing user photos.

.. figure:: images/features/user_profile.png
    :width: 600px
    :align: center

    Users of your Tethys Portal can update and maintain their profiles.

Customizable
------------

The home page of the Tethys Portal is completely customizable. Change the title and logo of the Tethys Portal for quick installation or clone the Django project to have more control over the look and feel.

.. figure:: images/features/customize_homepage.png
    :width: 600px
    :align: center

    Customize the content of the Tethys Portal home page.

Acknowledgements
================

This material is based upon work supported by the National Science Foundation under Grant No. 1135482