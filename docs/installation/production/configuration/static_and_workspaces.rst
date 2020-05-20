.. _production_static_workspaces_dirs:

*********************************
Static and Workspaces Directories
*********************************

**Last Updated:** May 2020

7) Make Directories for Workspaces and Static Files

    Get the values of the static and workspace directories in settings:

    .. code-block::

        tethys settings --get STATIC_ROOT
        tethys settings --get TETHYS_WORKSPACES_ROOT

    Create the directories if they do not already exist

    .. code-block::

        mkdir -p <STATIC_ROOT>
        mkdir -p <TETHYS_WORKSPACE_ROOT>

8) Collect Static Files and App Workspaces:

    .. code-block::

        tethys manage collectall --noinput

    .. tip::

        The ``tethys manage collectall`` command is equivalent of:

        .. code-block::

            tethys manage collectstatic
            tethys manage collectworkspaces

Static Directory
================

App Workspaces Directory
========================

.. tip::

    Backup this directory

Collect Static and Workspace Files
==================================