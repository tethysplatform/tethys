********************
Upgrade to |version|
********************

**Last Updated:** December 2018

This document provides a recommendation for how to upgrade Tethys Platform from the last release version. If you have not updated Tethys Platform to the last release version previously, please revisit the documentation for that version and follow those upgrade instructions first.


1. Activate Tethys environment and start your Tethys Database:

::

    . t
    tstartdb

2. Backup your ``settings.py`` (Note: If you do not backup your ``settings.py`` you will be prompted to overwrite your settings file during upgrade):

::

    mv $TETHYS_HOME/src/tethys_portal/settings.py $TETHYS_HOME/src/tethys_portal/settings_20.py

.. caution::

    Don't forget to copy any settings from the backup settings script (``settings.py_bak``) to the new settings script. Common settings that need to be copied include:

    * DEBUG
    * ALLOWED_HOSTS
    * DATABASES, TETHYS_DATABASES
    * STATIC_ROOT, TETHYS_WORKSPACES_ROOT
    * EMAIL_HOST, EMAIL_PORT, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD, EMAIL_USE_TLS, DEFAULT_FROM_EMAIL
    * SOCIAL_OAUTH_XXXX_KEY, SOCIAL_OAUTH_XXXX_SECRET
    * BYPASS_TETHYS_HOME_PAGE

3. (Optional) If you want the new environment to be called ``tethys`` remove the old environment:

::

    conda activate base
    conda env remove -n tethys

.. tip::

    If these commands don't work, you may need to update your conda installation:

    ::

        conda update conda -n root -c defaults

4. Download and execute the new install tethys script with the following options (Note: if you removed your previous tethys environment, then you can omit the ``-n tethys21`` option to have the new environment called ``tethys``):

.. parsed-literal::

    wget :install_tethys:`sh`
    bash install_tethys.sh -b |branch| --partial-tethys-install cieast -n tethys21

5. (Optional) If you have a locally installed database server then you need to downgrade postgresql to the version that the database was created with. If it was created by the 2.0 Tethys install script then it was created with postgresql version 9.5. (Note: be sure to open a new terminal so that the newly created tethys environment is activated):

::

    t
    conda install -c conda-forge postgresql=9.5


.. tip::

    These instructions assume your previous installation was done using the install script with the default configuration. If you used any custom options when installing the environment initially, you will need to specify those same options. For an explanation of the installation script options, see: :ref:`install_script_options`.












