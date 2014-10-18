**************
App Harvesting
**************

**Last Updated:** May 20, 2014

The Tethys Apps plugin requires app projects to conform to a specific file structure. To understand why the structure of an apps project is important, it is useful to know how apps are loaded into CKAN by the Tethys Apps plugin.

Apps are loaded when the CKAN server starts up by a process called App Harvesting (see :ref:`harvest-figure-1`). This task is performed by an instance of the ``SingletonAppHarvester`` class called the :term:`app harvester`. When CKAN loads, the Tethys Apps plugin creates a new :term:`app harvester`. The :term:`app harvester` walks through each of the :term:`app packages` in the :file:`ckanapp` directory and locates the app configuration file (:file:`app.py`). This file contains the information that CKAN needs to load the app.

After the :term:`app harvester` has located all of the app configuration files, it creates an instance each class, which will be referred to as :term:`app instances`, hereafter. The :term:`app harvester` calls all of the methods of each :term:`app instance` and passes itself as the only argument. These methods pass information about the app to the :term:`app harvester`. Finally, the Tethys Apps plugin uses the information the :term:`app harvester` has collected from the apps to load the apps into CKAN.

.. _harvest-figure-1:

.. figure:: images/app_harvest.png
	:alt: diagram of app harvesting process

	**Figure 1. The app harvesting process.**

AppBase Class
=============

The app harvesting process is made to mimic the process by which plugins for CKAN are written. The :term:`app class` is implemented in :file:`app.py` is an instance of the ``AppBase`` class that is provided by the Tethys Apps plugin. The data that is declared in this the :term:`app class` and collected by the :term:`app harvester` is eventually passed as parameters to the CKAN plugin interface methods of the Tethys Apps plugin. :ref:`harvest-figure-2` shows how app classes and CKAN classes mirror each other.

.. _harvest-figure-2:

.. figure:: images/mirror_comparison.png
	:alt: comparison of the CKAN plugin class and a Tethys Apps class

	**Figure 2. Comparison of a CKAN Plugin class and a Tethys App class.**

As an example, compare the ``after_map`` plugin method and the ``registerController`` app method. The ``registerController`` method receives the :term:`app harvester` and calls ``addControllers`` on it to add the appropriate parameters to map a controller in Pylons. The Tethys Apps plugin ``after_map`` class is given the ``map`` object that is used to map all of the controllers for the CKAN site. The plugin class retrieves the controller information collected by the harvester and passes it as parameters to the ``connect`` method of ``map``.

In summary, the purpose these mirror methods of the :term:`app class` in :file:`app.py` is to collect the data that the Tethys Apps plugin needs to connect the app to CKAN. The :term:`app harvester` aggregates all of this information from all of the :term:`app instances` and passes it along to the Tethys Apps plugin. More detail will be given about the structure of app projects and the :file:`app.py` class in a later section.

.. note::
	Only the methods that are mirrored between a plugin class and an app class are shown in :ref:`harvest-figure-2`. Both classes have other methods that are not related that are not shown.
