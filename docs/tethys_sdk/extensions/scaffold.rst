*************************
Scaffold and Installation
*************************

**Last Updated:** February 22, 2018

Scaffolding an Extension
------------------------

Scaffolding Tethys Extensions is done in the same way scaffolding of apps is performed. Just specify the extension option when scaffolding:

::

    tethys scaffold -e my_first_extension

Installing an Extension
-----------------------

This will create a new directory called ``tethysext-my_first_extension``. To install the extension for development into your Tethys Portal:

::

    cd tethysext-my_first_extension
    tethys install -d

Alternatively, to install the extension on a production Tethys Portal:

::

    cd tethysext-my_first_extension
    tethys install

If the installation was successful, you should see something similar to this when Tethys Platform loads:

::

    Loading Tethys Extensions...
    Tethys Extensions Loaded: my_first_extension

You can also confirm the installation of an extension by navigating to the *Site Admin* page and selecting the ``Installed Extensions`` link under the ``Tethys Apps`` heading.

Uninstalling an Extension
-------------------------

An extension can be easily uninstalled using the ``uninstall`` command provided in the Tethys CLI:

::

    tethys uninstall -e my_first_extension

