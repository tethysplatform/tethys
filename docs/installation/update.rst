********************
Upgrade to |version|
********************

**Last Updated:** December 2018

This document provides a recommendation for how to upgrade Tethys Platform from the last release version. If you have not updated Tethys Platform to the last release version previously, please revisit the documentation for that version and follow those upgrade instructions first.


Upgrade using the Install Script
--------------------------------

Run the following commands from a terminal to download and run the Tethys Platform install script.

For systems with `wget` (most Linux distributions):

1. Upgrade using new Python 3 Environment (recommended)
=======================================================

.. parsed-literal::

    . t && conda activate base
    conda env remove -n tethys
    conda deactivate
    wget :install_tethys:`sh`
    bash install_tethys.sh --partial-tethys-install cesiat -b |branch|

For Systems with `curl` (e.g. Mac OSX and CentOS):

.. parsed-literal::

    . t && conda activate base
    conda env remove -n tethys
    conda deactivate
    curl :install_tethys:`sh` -o ./install_tethys.sh
    bash install_tethys.sh --partial-tethys-install cesiat -b |branch|

2. Upgrade using existing Python 2 Environment (discouraged)
============================================================

.. parsed-literal::

    wget :install_tethys:`sh`
    bash install_tethys.sh --partial-tethys-install cusiat --python-version 2 -b |branch|

For Systems with `curl` (e.g. Mac OSX and CentOS):

.. parsed-literal::

    curl :install_tethys:`sh` -o ./install_tethys.sh
    bash install_tethys.sh --partial-tethys-install cusiat --python-version 2 -b |branch|

.. warning::

    Python 2 support is officially deprecated in this release. It will no longer be supported in the next release of Tethys Platform. Migrate now!


.. tip::

    These instructions assume your previous installation was done using the install script with the default configuration. If you used any custom options when installing the environment initially, you will need to specify those same options. For an explanation of the installation script options, see: :ref:`install_script_options`.


Upgrade Manually
----------------

1. Get the Latest Version
=========================

Change into the directory containing your Tethys Platform installation (tethys_home). The default location is ``~/tethys/src``:

::

    $ cd <tethys_home>
    $ git pull origin |branch|

2. Upgrade or Create New Environment
====================================

a. Upgrade Conda Dependencies

    Install new dependencies and upgrade old ones:

    ::

                 $ . t
        (tethys) $ conda env update -f environment_py<version>.yml
        (tethys) $ python setup.py develop

    **OR**

b. Create new Conda Environment

    Remove the old environment:

    ::

                $ .t && conda activate base
         (base) $ conda env remove -n tethys

    Create new Python 3 environment (recommended):

    ::

         (base) $ conda env create -f environment_py3.yml
         (base) $ conda activate tethys
       (tethys) $ python setup.py develop

    **OR**

    Create new Python 2 environment (discouraged):

    ::

         (base) $ conda env create -f environment_py2.yml
         (base) $ conda activate tethys
       (tethys) $ python setup.py develop

    .. warning::

        Python 2 support is officially deprecated in this release. It will no longer be supported in the next release of Tethys Platform. Migrate now!


3. Generate New Settings Script
===============================

Backup your old settings script (``settings.py``) and generate a new settings file to get the latest version of the settings. Then copy any settings (like database usernames and passwords) from the backed up settings script to the new settings script.

::

    (tethys) $ mv ./tethys_portal/settings.py ./tethys_portal/settings.py_bak
    (tethys) $ tethys gen settings -d tethys_portal

.. caution::

    Don't forget to copy any settings from the backup settings script (``settings.py_bak``) to the new settings script. Common settings that need to be copied include:

    * DEBUG
    * ALLOWED_HOSTS
    * DATABASES, TETHYS_DATABASES
    * STATIC_ROOT, TETHYS_WORKSPACES_ROOT
    * EMAIL_HOST, EMAIL_PORT, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD, EMAIL_USE_TLS, DEFAULT_FROM_EMAIL
    * SOCIAL_OAUTH_XXXX_KEY, SOCIAL_OAUTH_XXXX_SECRET
    * BYPASS_TETHYS_HOME_PAGE

4. Sync the Database
====================

Start the database you have been using for your Tethys Portal if it is not already running. Then migrate the Tethys database as follows:

::

    (tethys) $ tethys manage syncdb

5. Create Shortcuts
===================

Use the new install script to create shortcuts for your new environment:

::

    (tethys) $ cd scripts
    (tethys) $ install_tethys.sh --partial-tethys-install at