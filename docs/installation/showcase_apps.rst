.. _installation_showcase_apps:

*************
Showcase Apps
*************

**Last Updated:** September 2025

Starting in Tethys Platform 4.0, the Developer Tools pages were removed from the Tethys Portal including the Gizmo Showcase page. Two new Tethys Apps were developed to replace the Gizmo Showcase including the Gizmo Showcase App and the Layout Showcase App. These apps can easily be installed into any Tethys Portal and provide live demos and code examples of all of the Tethys Gizmos and Layouts, respectively. Use the instructions below to install each app and view the code.

.. _installation_gizmo_showcase_app:

Gizmo Showcase App
==================

The Gizmo Showcase App provides live demonstrations and code examples of every Gizmo.

.. figure:: ./resources/gizmo_showcase_app.png
    :width: 800px
    :align: center

Live Demo
---------

You can try the Tethys Gizmos Showcase App online on the `Tethys Demo Portal <https://demo.tethysgeoscience.org/apps/gizmo-showcase/>`_.

Source Code
-----------

The source code can be viewed on GitHub:

* https://github.com/tethysplatform/tethysapp-gizmo_showcase

Installation
------------

1. Download Code

    .. code-block:: bash

        git clone https://github.com/tethysplatform/tethysapp-gizmo_showcase.git

2. Run ``tethys install``:

    .. code-block:: bash

        cd tethysapp-gizmo_showcase
        tethys install

3. Download sample data for Bokeh plots (first time only)

    .. code-block:: bash

        python
        >>> import bokeh
        >>> bokeh.sampledata.download()

4. Set up Cesium Ion Token (Optional)

    To view the Cesium Map View demos, you will need to obtain a Cesium Ion Token. See Cesium ion Access Tokens tutorial for instructions on obtaining a token. After obtaining a token, navigate to the settings for the Gizmo Showcase, locate the cesium_ion_token setting under Custom Settings section, enter the token, and save.

5. GeoServer (Optional)

    The Gizmo Showcase has a Spatial Dataset Service Setting that can be used to link a GeoServer service into the app. When included, the Map View Gizmo and the WMS Cesium demo will display the US States layer. Any GeoServer can be used, so long as it contains the demo layers. See :ref:`assign_spatial_dataset_service` for how to add a GeoServer as a Spatial Dataset Service and link it to an app.


.. _installation_layout_showcase_app:

Layout Showcase App
===================

The Layout Showcase App provides live demonstrations and code examples of each Tethys Layout.

.. figure:: ./resources/layout_showcase_app.png
    :width: 800px
    :align: center

Source Code
-----------

The source code can be viewed on GitHub:

* https://github.com/tethysplatform/tethysapp-layout_showcase

Live Demo
---------

You can try the app Tethys Layout Showcase App online on the `Tethys Demo Portal <https://demo.tethysgeoscience.org/apps/layout-showcase/>`_.

Installation
------------

1. Download Code

    .. code-block:: bash

        git clone https://github.com/tethysplatform/tethysapp-layout_showcase.git

2. Run ``tethys install``:

    .. code-block:: bash

        cd tethysapp-layout_showcase
        tethys install

3. OpenCage Geocoding API Key (Optional)

    The Map Layout includes a reverse geocoding capability (address search) that is powered by the `OpenCage Geocoding API <https://opencagedata.com/>`_. To enable this feature in the demo you will need to acquire an OpenCage API key. Use their `Quick Start <https://opencagedata.com/api#quickstart>`_ guide to learn how to obtain an API key. Then enter the API key in the ``geocode_api_key`` setting of the app.

4. GeoServer (Optional)

    The Layout Showcase App has a Spatial Dataset Service Setting that can be used to link a GeoServer service to the app. When included, the Map Layout demo will display the US States layer hosted by GeoServer. Any GeoServer can be used, so long as it contains the demo layers. See :ref:`assign_spatial_dataset_service` for how to add a GeoServer as a Spatial Dataset Service and link it to an app.