.. _production_static_workspaces_dirs:

*********************************
Static and Workspaces Directories
*********************************

**Last Updated:** October 2024

1. Create Static Directory
==========================

Static files include all files in the ``public`` or ``static`` directories of Tethys Portal and apps and examples include JavaScript, CSS, and images. As the name implies, static files are not dynamically generated and can be served directly by NGINX, which will be able to do so much more efficiently than the Daphne-Django server could. You will need to collect all of the static files into one directory for NGINX to be able to more easily host them. This can be done as follows:

1. Get the value of the static directory from the `STATIC_ROOT <https://docs.djangoproject.com/en/5.0/ref/settings/#static-root>`_ setting:

    .. code-block::

        tethys settings --get STATIC_ROOT

    .. tip::

        You may set the ``STATIC_ROOT`` variable to point at whichever directory you would like as follows:

        .. code-block::

            tethys settings --set STATIC_ROOT /my/custom/static/directory

2. Create the static directory if it does not already exist

    .. code-block::

        sudo mkdir -p <STATIC_ROOT>
        sudo chown -R $USER <STATIC_ROOT>

    .. note::

        Replace ``<STATIC_ROOT>`` with the value returned by the previous command (see step 1.1).

3. Collect the static files to the ``STATIC_ROOT`` location:

    .. code-block::

        tethys manage collectstatic

2. Create App Workspaces Directory
==================================

The app workspaces directory is one location where all app workspaces are collected. The app workspaces typically store files that are generated by the app while it is being used and often this data needs to be preserved. Collecting all of the workspaces of apps to a single location makes it easier to provision storage for the workspaces and backup the data contained therein. Setup the app workspace directory as follows:

1. Get the value of the static directory from the ``TETHYS_WORKSPACES_ROOT`` setting:

    .. code-block::

        tethys settings --get TETHYS_WORKSPACES_ROOT

    .. tip::

        You may set the ``TETHYS_WORKSPACES_ROOT`` variable to point at whichever directory you would like as follows:

        .. code-block::

            tethys settings --set TETHYS_WORKSPACES_ROOT /my/custom/static/directory

2. Create the workspaces directory if it does not already exist

    .. code-block::

        sudo mkdir -p <TETHYS_WORKSPACES_ROOT>
        sudo chown -R $USER <TETHYS_WORKSPACES_ROOT>

   .. note::

        Replace ``<TETHYS_WORKSPACES_ROOT>`` with the value returned by the previous command (see step 2.1).

.. tip::

    The ``TETHYS_WORKSPACES_ROOT`` directory is one of the recommended directories to backup.

.. warning::

    The following step is deprecated in Tethys 4.3 and is not required when using the :ref:`tethys_paths_api`. It will no longer be available in Tethys 5.0.

3. Collect the app workspaces to the ``TETHYS_WORKSPACES_ROOT`` location:

    .. code-block::

        tethys manage collectworkspaces

.. tip::

    You can collect both the static files and the app workspaces with a single command:

    .. code-block::

        tethys manage collectall


3. Create App Media Directory
=============================

The app media directory is a location where apps can store files uploaded by users to make them publicly accesible. Setup the app media directory as follows:

1. Get the value of the static directory from the ``MEDIA_ROOT`` setting:

    .. code-block::

        tethys settings --get MEDIA_ROOT

    .. tip::

        You may set the ``MEDIA_ROOT`` variable to point at whichever directory you would like as follows:

        .. code-block::

            tethys settings --set MEDIA_ROOT /my/custom/static/directory

2. Create the media directory if it does not already exist

    .. code-block::

        sudo mkdir -p <MEDIA_ROOT>
        sudo chown -R $USER <MEDIA_ROOT>

   .. note::

        Replace ``<MEDIA_ROOT>`` with the value returned by the previous command (see step 2.1).

.. tip::

    The ``MEDIA_ROOT`` directory is one of the recommended directories to backup.
