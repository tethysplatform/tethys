********
Features
********

**Last Updated:** May 28, 2015

Tethys is a platform that can be used to develop and host engaging, interactive water resources web applications or web apps. It includes a suite of free and open source software (FOSS) that has been carefully selected to address the unique development needs of water resources web apps. Tethys web apps are developed using a Python software development kit (SDK) which includes programmatic links to each software component. Tethys Platform is powered by the `Django <https://www.djangoproject.com/>`_ Python web framework giving it a solid web foundation with excellent security and performance.

.. figure:: images/features/example_app_page.png
    :width: 600px
    :align: center

**Tethys platform can be used to create engaging, interactive web apps for water resources.**


Software Suite
==============

Tethys Platform provides a suite of free and open source software. Included in the :doc:`./software_suite` is `PostgreSQL <http://www.postgresql.org/>`_ with the `PostGIS <http://postgis.net/>`_ extension for spatial database storage, `GeoServer <http://geoserver.org/>`_ for spatial data publishing, and `52 North WPS <http://52north.org/communities/geoprocessing/wps/>`_ for geoprocessing. Tethys also provides Gizmos for inserting `OpenLayers <http://openlayers.org/>`_ and `Google Maps <https://developers.google.com/maps/web/>`_ for interactive spatial data visualizations in your web apps. The :doc:`./software_suite` also includes `HTCondor <http://research.cs.wisc.edu/htcondor/>`_ for managing distributed computing resources and scheduling computing jobs.

.. figure:: images/features/tethys_platform_diagram.png
    :width: 600px
    :align: center

**Tethys Platform include software to meet water resources web app development needs.**

.. note::

    Read more about the Software Suite by reading the :doc:`./software_suite` documentation.


Python Software Development Kit
===============================

Tethys web apps are developed with the `Python programming language <https://www.python.org/>`_ and a :doc:`./tethys_sdk` (SDK). Tethys web apps projects are organized using a model-view-controller (MVC) approach. The SDK provides Python module links to each software component of the Tethys Platform, making the functionality of each software easy to incorporate each in your web apps. In addition, you can use all of the Python modules that you are accustomed to using in your scientific Python scripts to power your web apps.

.. figure:: images/features/app_code.png
    :width: 600px
    :align: center

**Tethys web apps are developed using Python and the Tethys SDK.**

.. note::

    Read more about the Tethys SDK by reading the :doc:`./tethys_sdk` documentation.

Templating and Gizmos
=====================

Tethys SDK takes advantage of the Django template system so you can build dynamic pages for your web app while writing less HTML. It also provides a series of modular user interface elements called Gizmos. With only a few lines of code you can add range sliders, toggle switches, auto completes, interactive maps, and dynamic plots to your web app.

.. figure:: images/features/example_gizmo.png
    :width: 600px
    :align: center

**Insert common user interface elements like date pickers, maps, and plots with minimal coding.**

.. note::

    Read more about templating and Gizmo by reading the :doc:`./tethys_sdk/templating` and the :doc:`./tethys_sdk/gizmos` documentation.

Tethys Portal
=============

Tethys Platform includes a modern web portal built on Django that is used to host web apps called :doc:`tethys_portal`. It provides the core website functionality that is often taken for granted in modern web applications including a user account system with with a password reset mechanism for forgotten passwords. It provides an administrator backend that can be used to manage user accounts, permissions, link to elements of the software suite, and customize the instance.

The portal also includes landing page that can be used to showcase the capabilities of the Tethys Platform instance and an app library page that serves as the access point for installed apps. The homepage and theme of Tethys Portal are customizable allowing organizations to re-brand it to meet the their needs.

.. figure:: images/features/apps_library.png
    :width: 600px
    :align: center

**Browse available web apps using the Apps Library.**

.. note::

    Read more about the Tethys Portal by reading the :doc:`./tethys_portal` documentation.

Computing
=========

Tethys Platform includes Python modules that allow you to provision and run computing jobs in distributed computing environments. With CondorPy you can define your computing jobs and submit them to distributed computing environments provided by `HTCondor <http://research.cs.wisc.edu/htcondor/>`_.

.. figure:: images/features/computing_condorpy.png
    :width: 400px
    :align: center

**CondorPy enables computing jobs to be created and submitted to a HTCondor computing pool.**

HTCondor provides a way to make use of the idle computing power that is already available in your office.

.. note::

    To learn more, read the :doc:`./tethys_sdk/jobs` and the :doc:`./tethys_sdk/compute`.


Acknowledgements
================

This material is based upon work supported by the National Science Foundation under Grant No. 1135482