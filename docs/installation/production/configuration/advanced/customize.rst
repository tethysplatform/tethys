.. _production_customize_theme:

************************************
Customize Portal Theme (Recommended)
************************************

**Last Updated:** May 2020

The content of Tethys Portal can and should be customized or re-branded to reflect your organization. To access these settings, login to Tethys Portal using an administrator account and navigate to the **Site Admin** page. Then select the  **Site Settings** link under the **TETHYS PORTAL** heading. Site-wide settings can be changed using the **General Settings** link and the content on the home page can be modified by using the **Home Page** link.

General Settings
================

The following settings can be used to modify global features of the site.  Access the settings using the **Site Settings > General Settings** links on the admin pages.

========================== =================================================================================
Setting                    Description
========================== =================================================================================
Site Title                 Title of the web page that appears in browser tabs and bookmarks of the site.
Favicon                    Path to the image that is used in browser tabs and bookmarks.
Brand Text                 Title that appears in the header.
Brand Image                Logo or image that appears next to the title in the header.
Brand Image Height         Height to scale the brand image to.
Brand Image Width          Width to scale the brand image to.
Brand Image Padding        Adjust space above brand image to center it.
Apps Library Title         Title of the page that displays app icons.
Primary Color              Color that is used as the primary theme color  (e.g.: #ff0000 or rgb(255,0,0)).
Secondary Color            Color that is used as the secondary theme color.
Primary Text Color         Color of the text appearing in the headers and footer.
Primary Text Hover Color   Hover color of the text appearing in the headers and footer (where applicable).
Secondary Text Color       Color of secondary text on the home page.
Secondary Text Hover Color Hover color of the secondary text on the home page.
Background Color           Color of the background on the apps library page and other pages.
Footer Copyright           Copyright text that appears in the footer.
========================== =================================================================================

Home Page Settings
==================

The following settings can be used to modify the content on the home page. Access the settings using the **Site Settings > Home Page** links on the admin pages.

====================== =================================================================================
Setting                Description
====================== =================================================================================
Hero Text              Text that appears in the hero banner at the top of the home page.
Blurb Text             Text that appears in the blurb banner, which follows the hero banner.
Feature 1 Heading      Heading for 1st feature highlight.
Feature 1 Body         Body text for the 1st feature highlight.
Feature 1 Image        Path or url to image for the 1st feature highlight.
Feature 2 Heading      Heading for 2nd feature highlight.
Feature 2 Body         Body text for the 2nd feature highlight.
Feature 2 Image        Path or url to image for the 2nd feature highlight.
Feature 3 Heading      Heading for 3rd feature highlight.
Feature 3 Body         Body text for the 3rd feature highlight.
Feature 3 Image        Path or url to image for the 3rd feature highlight.
Call to Action         Text that appears in the call to action banner at the bottom of the page (only visible when user is not logged in).
Call to Action Button  Text that appears on the call to action button in the call to action banner (only visible when user is not logged in).
====================== =================================================================================

For more advanced customization, you may use the **Custom Styles** and **Custom Template** options to completely replace the Home Page or Apps Library page CSS and HTML.

Custom Styles
=============

The following settings can be used to add additional CSS to the Home page, Apps Library page, and portal-wide. Access the settings using the **Site Settings > Custom Styles** links on the admin pages.

====================== =================================================================================
Setting                Description
====================== =================================================================================
Portal Base CSS        CSS or path to a CSS file to be loaded on every Tethys Portal page. The file must be located within a valid static or public directory, such as in a Tethys app, Tethys extension, or Django app.
Home Page CSS          CSS or path to a CSS file to be loaded on the Home page. The file must be located within a valid static or public directory, such as in a Tethys app, Tethys extension, or Django app.
Apps Library CSS       CSS or path to a CSS file to be loaded on the Apps Library page. The file must be located within a valid static or public directory, such as in a Tethys app, Tethys extension, or Django app.
====================== =================================================================================

Custom Templates
================

The following settings can be used to override the templates for the Home page and Apps Library page. Access the settings using the **Site Settings > Custom Templates** links on the admin pages.

====================== =================================================================================
Setting                Description
====================== =================================================================================
Home Page Template     Path to alternate Home page template (will replace Home page template entirely). The template must be located within a valid templates directory, such as in a Tethys app, Tethys extension, or Django app.
Apps Library Template  Path to alternate Apps Library page template (will replace Apps Library page template entirely). The template must be located within a valid templates directory, such as in a Tethys app, Tethys extension, or Django app.
====================== =================================================================================


Bypass the Home Page
====================

Tethys Portal can also be configured to bypass the home page. When this setting is applied, the root url will always redirect to the apps library page. This setting is modified in the :file:`portal_config.yml` file. Simply set the ``BYPASS_TETHYS_HOME_PAGE`` setting to ``True``:

.. code-block:: yaml

  TETHYS_PORTAL_CONFIG:
    BYPASS_TETHYS_HOME_PAGE: True

Enable Open Signup
==================

You may also wish to enable open signup on your Tethys Portal. To do so, you must modify the ``ENABLE_OPEN_SIGNUP`` setting in the :file:`portal_config.yml` file:

.. code-block:: yaml

  TETHYS_PORTAL_CONFIG:
    ENABLE_OPEN_SIGNUP: True

.. warning::

    Enabling open signup will allow anyone to sign up for an account and could expose your site to exploitation by nefarious actors. Only enable this option if you plan to actively moderate users on your Tethys Portal.
