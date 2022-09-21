.. _production_customize_theme:

************************************
Customize Portal Theme (Recommended)
************************************

**Last Updated:** September 2022

The content of Tethys Portal can and should be customized or re-branded to reflect your organization. To access these settings, login to Tethys Portal using an administrator account and navigate to the **Site Admin** page. Then select the  **Site Settings** link under the **TETHYS PORTAL** heading. Site-wide settings can be changed using the **General Settings** link and the content on the home page can be modified by using the **Home Page** link.

For more information about the site settings that can be customized refer to :ref:`Tethys Portal Configuration: Site Settings <tethys_configuration_site_settings>`

.. _production_customize_bypass_home:

Bypass the Home Page
++++++++++++++++++++

Tethys Portal can also be configured to bypass the home page. When this setting is applied, the root url will always redirect to the apps library page. This setting is modified in the :file:`portal_config.yml` file. Simply set the ``BYPASS_TETHYS_HOME_PAGE`` setting to ``True``:

.. code-block:: yaml

  TETHYS_PORTAL_CONFIG:
    BYPASS_TETHYS_HOME_PAGE: True

.. _production_customize_enable_open:

Enable Open Signup
++++++++++++++++++

You may also wish to enable open signup on your Tethys Portal. To do so, you must modify the ``ENABLE_OPEN_SIGNUP`` setting in the :file:`portal_config.yml` file:

.. code-block:: yaml

  TETHYS_PORTAL_CONFIG:
    ENABLE_OPEN_SIGNUP: True

.. warning::

    Enabling open signup will allow anyone to sign up for an account and could expose your site to exploitation by nefarious actors. Only enable this option if you plan to actively moderate users on your Tethys Portal.

.. tip::

  To see a full list of settings that can be customized in the :file:`portal_config.yml` file refer to the :ref:`tethys_configuration` documentation.