********
Glossary
********

.. glossary::
    :sorted:

    app package
    app packages
        A Python namespace package of an :term:`app project` that contains all of the source code for an app. The app package is named the same as the app by convention. Refer to Figure 1 of :doc:`./app_project` for more information.

    app project
        All of the source code for a Tethys Apps app including the :term:`release package` and the :term:`app package`.

    release package
        The top level Python namespace package of an :term:`app project`. The release package contains the :term:`setup script` and all the source for an app including the :term:`app package`. Refer to Figure 1 of :doc:`./app_project` for more information.

    app harvester
        An instance of the ``SingletonAppHarvester`` class. The app harvester collects information about each app and uses it to connect the apps to CKAN. Refer to :doc:`app_harvesting`.

    app instance    
    app instances
        An instance of an :term:`app class`.

    app class
        A class defined in the :term:`app configuration file` that inherits from the ``AppBase`` class provided by the Tethys Apps plugin. This class implements several methods that are used to link apps with CKAN.

    snippet
    snippets
        Reusable view elements that can be inserted into a template using a single line of code. Examples include common GUI elements like buttons, toggle switches, and input fields as well as more complex elements like maps and plots.

    app configuration file
        A file located in the :term:`app package` and called :file:`app.py` by convention. This file contains the :term:`app class` that is used to configure apps. For more details on the app configuration file, see :doc:`./getting_started/configuration`.

    setup script
        A file located in the :term:`release package` and called :file:`setup.py` by convention. The setup script is used to automate the installation of apps. For more details see :doc:`./getting_started/distribution`.

    persistent store
    persistent stores
        A persistent store is a database that can be automatically created for an app. See :doc:`./getting_started/model` for more information about persistent stores.

    resource
    resources
        A resource is a file or other object and the associated metadata that is stored in a :term:`dataset service`.

    dataset
    datasets
        A dataset is a container for one or more resources that are stored in a :term:`dataset service`.

    dataset service
    dataset services
        A dataset service is a web service external to Tethys Platform that can be used to store and publish file-based datasets (e.g.: text files, Excel files, zip archives, other model files). See the :doc:`./tethys_api/dataset_services` for more information.

    virtual environment
    Python virtual environment
        An isolated Python installation. Many operating systems use the system Python installation to perform maintenance operations. Installing Tethys Platform in a virtual environment prevents potential dependency conflicts.

    Model View Controller
        The development pattern used to develop Tethys apps. The Model represents the data of the app, the View is composed of the representation of the data, and the Controller consists of the logic needed to prepare the data from the Model for the View and any other logic your app needs.