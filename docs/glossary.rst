********
Glossary
********

**Last Updated:** May 2017

.. glossary::
    :sorted:

    app package
    app packages
        A Python namespace package of a Tethys :term:`app project` that contains all of the source code for an app. The app package is named the same as the app by convention. Refer to Figure 1 of :doc:`./supplementary/app_project` for more information.

    app project
        All of the source code for a Tethys app including the :term:`release package` and the :term:`app package`.

    release package
        The top level Python namespace package of an :term:`app project`. The release package contains the :term:`setup script` and all the source for an app including the :term:`app package`. Refer to Figure 1 of :doc:`./supplementary/app_project` for more information.

    app harvester
        An instance of the ``SingletonAppHarvester`` class. The app harvester collects information about each app and uses it to load Tethys apps.

    app instance    
    app instances
        An instance of an :term:`app class`.

    app class
        A class defined in the :term:`app configuration file` that inherits from the ``TethysAppBase`` class provided by the Tethys Platform. For more details on the app class, see :doc:`./tethys_sdk/app_class`.

    Gizmo
    Gizmos
        Reusable view elements that can be inserted into a template using a single line of code. Examples include common GUI elements like buttons, toggle switches, and input fields as well as more complex elements like maps and plots. For more information on Gizmos, see :doc:`tethys_sdk/gizmos`.

    app configuration file
        A file located in the :term:`app package` and called :file:`app.py` by convention. This file contains the :term:`app class` that is used to configure apps. For more details on the app configuration file, see :doc:`./tethys_sdk/app_class`.

    setup script
        A file located in the :term:`release package` and called :file:`setup.py` by convention. The setup script is used to automate the installation of apps.

    persistent store
    persistent stores
        A persistent store is a database that can be automatically created for an app. See the :doc:`./tethys_sdk/tethys_services/persistent_store` for more information about persistent stores.

    resource
    resources
        A resource is a file or other object and the associated metadata that is stored in a :term:`dataset service`.

    dataset
    datasets
        A dataset is a container for one or more resources that are stored in a :term:`dataset service`.

    spatial dataset
    spatial datasets
        A spatial dataset is a file-based dataset that stores spatial data (e.g.: shapefiles, GeoTiff, ArcGrid, GRASS ASCII Grid).

    dataset service
    dataset services
        A dataset service is a web service external to Tethys Platform that can be used to store and publish file-based datasets (e.g.: text files, Excel files, zip archives, other model files). See the :doc:`./tethys_sdk/tethys_services/dataset_services` for more information.

    virtual environment
        An isolated Python installation. Many operating systems use the system Python installation to perform maintenance operations. Installing Tethys Platform in a virtual environment prevents potential dependency conflicts. 
    
    conda environment
        An isolated Python installation managed by `Conda <https://docs.conda.io/projects/conda/en/latest/index.html>`_, which does more than a standard virtual environment, such as providing its own package manager and installing/managing non-python dependencies (e.g. netCDF4, GDAL, arcgis). Packages are installed via ``conda install`` rather than ``pip install``.


    Model View Controller
        The development pattern used to develop Tethys apps. The Model represents the data of the app, the View is composed of the representation of the data, and the Controller consists of the logic needed to prepare the data from the Model for the View and any other logic your app needs.

    wps service
    wps services
        A WPS Service provides processes/geoprocesses as web services using the Open Geospatial Consortium Web Processing Service (WPS) standard.

    Debian
        Debian is a type of Linux operating system and many Linux distributions are based on it including Ubuntu. See `Linux Distributions <https://en.wikipedia.org/wiki/Linux_distribution>`_ for more information.