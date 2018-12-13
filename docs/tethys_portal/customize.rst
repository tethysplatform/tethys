*********
Customize
*********

**Last Updated:** August 4, 2015

The content of Tethys Portal can be customized or rebranded to reflect your organization. To access these settings, login to Tethys Portal using an administrator account and select the  ``Site Settings`` link under the ``Tethys Portal`` heading. Sitewide settings can be changed using the ``General Settings`` link and the content on the home page can be modified by using the ``Home Page`` link.

General Settings
================

The following settings can be used to modify global features of the site.  Access the settings using the ``Site Settings > General Settings`` links on the admin pages.

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

**Figure 2.** General settings for Tethys Portal.

Home Page Settings
==================

The following settings can be used to modify the content on the home page. Access the settings using the ``Site Settings > Home Page`` links on the admin pages.

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

Bypass the Home Page
====================

Tethys Portal can also be configured to bypass the home page. When this setting is applied, the root url will always redirect to the apps library page. This setting is modified in the ``settings.py`` script. Simply set the ``BYPASS_TETHYS_HOME_PAGE`` setting to ``True`` like so:

::

    BYPASS_TETHYS_HOME_PAGE = True

Enable Open Signup
==================

Prior to version 1.3.0, any visitor to a Tethys portal could signup for an account without administrator approval or in other words account signup was open. For version 1.3.0+ the open signup capability has been disabled by default for security reasons. To enable open signup, you must modify the ``ENABLE_OPEN_SIGNUP`` setting in the ``settings.py`` script:

::

    ENABLE_OPEN_SIGNUP = True

