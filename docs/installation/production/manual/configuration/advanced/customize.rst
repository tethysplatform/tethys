.. _production_customize_theme:

************************************
Customize Portal Theme (Recommended)
************************************

**Last Updated:** May 2020

The content of Tethys Portal can and should be customized or re-branded to reflect your organization. To access these settings, login to Tethys Portal using an administrator account and navigate to the **Site Admin** page. Then select the  **Site Settings** link under the **TETHYS PORTAL** heading. Site-wide settings can be changed using the **General Settings** link and the content on the home page can be modified by using the **Home Page** link.

GENERAL_SETTINGS
++++++++++++++++

============================== ================================================================================
Setting                        Description
============================== ================================================================================
SITE_TITLE                     Title of the web page that appears in browser tabs and bookmarks of the site. Default is "Tethys Portal".
FAVICON                        Local or external path to the icon that will display in the browser tab. We recommend storing the favicon in the static directory of tethys_portal. Default is "tethys_portal/images/default_favicon.png".
BRAND_TEXT                     Title that appears in the header of the portal. Default is "Tethys Portal".
BRAND_IMAGE                    Local or external path to the portal logo. We recommend storing the logo in the static directory of tethys_portal. Default is "tethys_portal/images/tethys-logo-75.png".
BRAND_IMAGE_HEIGHT             The height of the brand image.
BRAND_IMAGE_WIDTH              The width of the brand image.
BRAND_IMAGE_PADDING            The padding for the brand image.
APPS_LIBRARY_TITLE             Title of the page that displays app icons. Default is "Apps".
PRIMARY_COLOR                  The primary color for the portal theme. Default is #0a62a9.
SECONDARY_COLOR                The secondary color for the portal theme. Default is #7ec1f7.
PRIMARY_TEXT_COLOR             Color of the text appearing in the headers and footer.
PRIMARY_TEXT_HOVER_COLOR       Hover color of the text appearing in the headers and footer (where applicable).
SECONDARY_TEXT_COLOR           Color of secondary text on the home page.
SECONDARY_TEXT_HOVER_COLOR     Hover color of the secondary text on the home page.
BACKGROUND_COLOR               Color of the background on the apps library page and other pages.
FOOTER_COPYRIGHT               Copyright text that appears in the footer of the portal. Default is "Copyright © 2022 Your Organization".
HOME_PAGE_TEMPLATE             Path to alternate Home page template (will replace Home page template entirely). The template must be located within a valid templates directory, such as in a Tethys app, Tethys extension, or Django app.
APPS_LIBRARY_TEMPLATE          Path to alternate Apps Library page template (will replace Apps Library page template entirely). The template must be located within a valid templates directory, such as in a Tethys app, Tethys extension, or Django app.
LOGIN_PAGE_TEMPLATE            Path to alternate portal login page template (will replace login page template entirely). The template must be located within a valid templates directory, such as in a Tethys app, Tethys extension, or Django app.
REGISTER_PAGE_TEMPLATE         Path to alternate portal registration (or signup) page template (will replace signup page template entirely). The template must be located within a valid templates directory, such as in a Tethys app, Tethys extension, or Django app.
USER_PAGE_TEMPLATE             Path to alternate user profile page template (will replace user page template entirely). The template must be located within a valid templates directory, such as in a Tethys app, Tethys extension, or Django app.
USER_SETTINGS_PAGE_TEMPLATE    Path to alternate user settings (i.e. edit) page template (will replace settings page template entirely). The template must be located within a valid templates directory, such as in a Tethys app, Tethys extension, or Django app.
============================== ================================================================================

HOME_PAGE
+++++++++

============================== ================================================================================
Setting                        Description
============================== ================================================================================
HERO_TEXT                      Text that appears in the hero banner at the top of the home page. Default is "Welcome to Tethys Portal,\nthe hub for your apps.".
BLURB_TEXT                     Text that appears in the blurb banner, which follows the hero banner. Default is "Tethys Portal is designed to be customizable, so that you can host apps for your\norganization. You can change everything on this page from the Home Page settings.".
FEATURE_1_HEADING              Heading for 1st feature highlight (out of 3).
FEATURE_1_BODY                 Body text for the 1st feature highlight.
FEATURE_1_IMAGE                Path or url to image for the 1st feature highlight.
FEATURE_2_HEADING              Heading for 2nd feature highlight (out of 3).
FEATURE_2_BODY                 Body text for the 2nd feature highlight.
FEATURE_2_IMAGE                Path or url to image for the 2nd feature highlight.
FEATURE_3_HEADING              Heading for 3rd feature highlight (out of 3).
FEATURE_3_BODY                 Body text for the 3rd feature highlight.
FEATURE_3_IMAGE                Path or url to image for the 3rd feature highlight.
CALL_TO_ACTION                 Text that appears in the call to action banner at the bottom of the page (only visible when user is not logged in). Default is "Ready to get started?".
CALL_TO_ACTION_BUTTON          Text that appears on the call to action button in the call to action banner (only visible when user is not logged in). Default is "Start Using Tethys!".
============================== ================================================================================

CUSTOM_STYLES
+++++++++++++

============================== ================================================================================
Setting                        Description
============================== ================================================================================
PORTAL_BASE_CSS                CSS code to modify the Tethys Portal Base Page, which extends most of the portal pages (i.e. Home, Login, Developer, Admin, etc.). Takes or straight CSS code or a file path available through Tethys static files, such as in a Tethys app, Tethys extension, or Django app.
HOME_PAGE_CSS                  CSS code to modify the Tethys Portal Home Page. Takes or straight CSS code or a file path available through Tethys static files, such as in a Tethys app, Tethys extension, or Django app.
APPS_LIBRARY_CSS               CSS code to modify the Tethys Portal Apps Library. Takes or straight CSS code or a file path available through Tethys static files, such as in a Tethys app, Tethys extension, or Django app.
ACCOUNTS_BASE_CSS              CSS code to modify the base template for all of the accounts pages (e.g. login, register, change password, etc.). Takes or straight CSS code or a file path available through Tethys static files, such as in a Tethys app, Tethys extension, or Django app.
LOGIN_CSS                      CSS code to modify the Portal Login page. Takes or straight CSS code or a file path available through Tethys static files, such as in a Tethys app, Tethys extension, or Django app.
REGISTER_CSS                   CSS code to modify the Portal Registration page. Takes or straight CSS code or a file path available through Tethys static files, such as in a Tethys app, Tethys extension, or Django app.
USER_BASE_CSS                  CSS code to modify the base template for all of the user profile pages (e.g. user, settings, manage storage). Takes or straight CSS code or a file path available through Tethys static files, such as in a Tethys app, Tethys extension, or Django app.
============================== ================================================================================

CUSTOM_TEMPLATES
++++++++++++++++

============================== ================================================================================
Setting                        Description
============================== ================================================================================
HOME_PAGE_TEMPLATE             Path to alternate Home page template (will replace Home page template entirely). The template must be located within a valid templates directory, such as in a Tethys app, Tethys extension, or Django app.
APPS_LIBRARY_TEMPLATE          Path to alternate Apps Library page template (will replace Apps Library page template entirely). The template must be located within a valid templates directory, such as in a Tethys app, Tethys extension, or Django app.
LOGIN_PAGE_TEMPLATE            Path to alternate portal login page template (will replace login page template entirely). The template must be located within a valid templates directory, such as in a Tethys app, Tethys extension, or Django app.
REGISTER_PAGE_TEMPLATE         Path to alternate portal registration (or signup) page template (will replace signup page template entirely). The template must be located within a valid templates directory, such as in a Tethys app, Tethys extension, or Django app.
USER_PAGE_TEMPLATE             Path to alternate user profile page template (will replace user page template entirely). The template must be located within a valid templates directory, such as in a Tethys app, Tethys extension, or Django app.
USER_SETTINGS_PAGE_TEMPLATE    Path to alternate user settings (i.e. edit) page template (will replace settings page template entirely). The template must be located within a valid templates directory, such as in a Tethys app, Tethys extension, or Django app.
============================== ================================================================================


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