***************
Add a Home Page
***************

**Last Updated:** July 2024

In this tutorial you will create a home page for the Google Earth Engine app that you created in :ref:`google_earth_engine_part_1`. This page will contain introductory information about that app. This will involve moving the current "home page", which contains the map viewer, to a new endpoint. Then you will set up a new controller and template for the new home page. The following topics will be reviewed in this tutorial:

* Adding a new view to your app
* Responsive web design using Bootstrap
* Bootstrap Grid System
* Bootstrap Fluid Containers
* Custom styling with CSS
* Linking to other pages and navigation
* Placeholder content for development: lorem ipsum and images

.. figure:: ../../../images/tutorial/gee/home_page.png
    :width: 800px
    :align: center

0. Start From Previous Solution (Recommended)
=============================================

We recommend you use the previous solution as a starting point for Part 2:

.. parsed-literal::

    git clone https://github.com/tethysplatform/tethysapp-earth_engine
    cd tethysapp-earth_engine
    git checkout -b plot-data-solution plot-data-solution-|version|

1. Move Map View to Viewer Endpoint
===================================

Currently, the map viewer page is the "home" page of the app as evidenced by it being rendered by a controller called ``home`` and a template called :file:`home.html`. In this step you will rename these to "viewer" to make way for the new home page. You will also change it's endpoint from the root endpoint to a new endpoint to allow the new home page to use the root endpoint.

1. Rename :file:`templates/earth_engine/home.html` to :file:`templates/earth_engine/viewer.html`.

2. Rename ``home`` controller to ``viewer`` in :file:`controllers.py`:

.. code-block:: python

    @controller
    def viewer(request):
        """
        Controller for the app viewer page.
        """

3. Change the ``render`` call at the end of the ``viewer`` controller to use the new :file:`templates/earth_engine/viewer.html` in :file:`controllers.py`:

.. code-block:: python

    return App.render(request, 'viewer.html', context)

4. Set custom URLs for the ``get_image_collection`` and  ``get_time_series_plot`` controllers in :file:`controllers.py`: so that their URLs are relative to the ``viewer`` url:

.. code-block:: python

    @controller(url='viewer/get-image-collection')
    def get_image_collection(request):
        ...

.. code-block:: python

    @controller(url='viewer/get-time-series-plot')
    def get_time_series_plot(request):
        ...

2. Create New Home Endpoint
===========================

In this step you will create a new ``home`` controller and :file:`home.html` template for the new home page.

1. Create a new :file:`templates/earth_engine/home.html` with the following contents:

.. code-block:: html+django

    {% extends tethys_app.package|add:"/base.html" %}
    {% load static tethys %}

    {% block app_content %}
    <h1>Home Page</h1>
    {% endblock %}

2. Create a new ``home`` controller in :file:`controllers.py`:

.. code-block:: python

    @controller
    def home(request):
        """
        Controller for the app home page.
        """
        context = {}
        return App.render(request, 'home.html', context)

3. Navigate to `<http://localhost:8000/apps/earth-engine/>`_ and verify that the new home page loads with text "Home Page".

4. Exit the app and launch it again from the Apps Library to verify that loads the new home page.

5. Navigate to `<http://localhost:8000/apps/earth-engine/viewer/>`_ and verify that the map view still functions as it should. Be sure to test loading a dataset or two and plot data at a location.


3. Remove Navigation from Home Page
===================================

As the app is not very complex (i.e. it only has two pages), the navigation menu will not be needed. Tethys Platform provides a variety of base templates including several without the navigation menu (see: :ref:`additional_base_templates`). In this step you remove the app navigation menu by changing the base template used by ``home.html``.

1. Change the ``extends`` tag in :file:`templates/earth_engine/home.html` to use the base template called ``app_header_content.html``:

.. code-block:: diff

   -{% extends tethys_app.package|add:"/base.html" %}
   +{% extends "tethys_apps/app_header_content.html" %}
    {% load static tethys %}

    {% block app_content %}
    <h1>Home Page</h1>
    {% endblock %}

2. Navigate to `<http://localhost:8000/apps/earth-engine/>`_ and verify that the navigation menu is gone.

4. Layout Home Page Grid with Bootstrap
=======================================

In this step, you will create a responsive two column layout using the `Bootstrap Grid System <https://getbootstrap.com/docs/5.2/layout/grid/>`_, which is part of the `Bootstrap CSS framework <https://getbootstrap.com/docs/5.2/getting-started/introduction/>`_. Bootstrap provides a number of simple recipes for implementing common HTML + CSS patterns. It is built-in with Tethys Platform, so no additional installation is required. 

1. Create a ``<div>`` element with class ``container-fluid`` in the ``app_content`` block:

.. code-block:: html+django
    :emphasize-lines: 2-3

    {% block app_content %}
    <div id="home-content-container" class="container-fluid">
    </div>
    {% endblock %}
    
.. note::

    The ``container-fluid`` allows the width of the container to grow and shrink dynamically or fluidly with screen size. It also has smaller margins than the normal ``container`` class.

2. Add a ``<div>`` element with class ``row``:

.. code-block:: html+django
    :emphasize-lines: 3-4

    {% block app_content %}
    <div  id="home-content-container" class="container-fluid">
      <div class="row">
      </div>
    </div>
    {% endblock %}

3. Add two column ``<div>`` elements with widths of 2/3rds (**8**/12ths) and 1/3rd (**4**/12ths) the width of the container, respectively:

.. code-block:: html+django
    :emphasize-lines: 4-7

    {% block app_content %}
    <div  id="home-content-container" class="container-fluid">
      <div class="row">
        <div class="col-md-8">
        </div>
        <div class="col-md-4">
        </div>
      </div>
    </div>
    {% endblock %}
    
.. note::

    Each row in a Bootstrap Grid can be divided into as many as 12 columns by specifying different numbers at the end of the ``col-md-X`` classes. A column of size 1 is effectively 1/12th of the width of the row. For example, to divide a row into two equal columns you would add two columns with size of 6 (6/12ths).
    
    Our home page has two columns but instead of being evenly divided, one of them takes up 8 of the available 12 column widths and the other takes the remaining 4 column widths. This effectively give our columns a 2 to 1 ratio. 


4. Add two rows to the second column, each containing a full-width (**12**/12) column:

.. code-block:: html+django
    :emphasize-lines: 7-14

    {% block app_content %}
    <div  id="home-content-container" class="container-fluid">
      <div class="row">
        <div class="col-md-8">
        </div>
        <div class="col-md-4">
          <div class="row">
            <div class="col-md-12">
            </div>
          </div>
          <div class="row">
            <div class="col-md-12">
            </div>
          </div>
        </div>
      </div>
    </div>
    {% endblock %}

5. Add container ``<div>`` elements with the ids ``about-container``, ``resources-container``, and ``get-started-container`` to each terminating column. Also add the ``info-container`` class to each of these ``<div>`` elements to allow for consistent styling in a later step:

.. code-block:: html+django
    :emphasize-lines: 5-6,11-12,17-18

    {% block app_content %}
    <div  id="home-content-container" class="container-fluid">
      <div class="row">
        <div class="col-md-8">
          <div id="about-container" class="info-container">
          </div>
        </div>
        <div class="col-md-4">
          <div class="row">
            <div class="col-md-12">
              <div id="resources-container" class="info-container">
              </div>
            </div>
          </div>
          <div class="row">
            <div class="col-md-12">
              <div id="get-started-container" class="info-container">
              </div>
            </div>
           </div>
        </div>
      </div>
    </div>
    {% endblock %}

5. Create About Panel Content
=============================

In this step we'll add a the title and some filler content to the About panel of the home page. The filler content was generated using a `Lorem Ipsum <https://loremipsum.io/>`_ generator. This is a commonly used strategy that allows the developer to test the structure and style of the page even if the content has not been finalized yet.

1. Add the title, "About", and a few paragraphs of filler text (lorem ipsum) to the ``<div>`` element with id ``about-container``. Use the ``info-title`` class on the title element to allow for consistent styling of all the titles in a later step. Place the placeholder filler text in ``<p>`` elements:

.. code-block:: html+django
    :emphasize-lines: 2-4

    <div id="about-container" class="info-container">
      <h2 class="info-title">About</h2>
      <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Eget est lorem ipsum dolor sit amet. Morbi tincidunt augue interdum velit euismod in pellentesque.</p>
      <p>Ac felis donec et odio pellentesque. Quis ipsum suspendisse ultrices gravida dictum fusce ut. Curabitur gravida arcu ac tortor dignissim convallis aenean et tortor. Sed euismod nisi porta lorem mollis. Nisi scelerisque eu ultrices vitae. Sit amet consectetur adipiscing elit duis. At in tellus integer feugiat scelerisque varius morbi enim.</p>
    </div>


2. Download :download:`this screenshot <./resources/earth-engine-viewer.png>` or take your own screenshot of the Earth Engine app and save it as :file:`public/images/earth-engine-viewer.png`.

3. Add the screenshot to the ``<div>`` element with id ``about-container``. Use the built-in ``static`` tag to get the path to the image:

.. code-block:: html+django
    :emphasize-lines: 5

    <div id="about-container" class="info-container">
      <h2 class="info-title">About</h2>
      <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Eget est lorem ipsum dolor sit amet. Morbi tincidunt augue interdum velit euismod in pellentesque.</p>
      <p>Ac felis donec et odio pellentesque. Quis ipsum suspendisse ultrices gravida dictum fusce ut. Curabitur gravida arcu ac tortor dignissim convallis aenean et tortor. Sed euismod nisi porta lorem mollis. Nisi scelerisque eu ultrices vitae. Sit amet consectetur adipiscing elit duis. At in tellus integer feugiat scelerisque varius morbi enim.</p>
      <img id="feature-image" src="{% static tethys_app|public:'images/earth-engine-viewer.png' %}">
    </div>

4. Navigate to `<http://localhost:8000/apps/earth-engine/>`_ and verify that the title "About", filler paragraphs, and screenshot appear in the panel on the left.


6. Create Resources Panel Content
=================================

In this step we'll add the content to the Resources panel of the home page. The Resources panel needs to contain a list of links to external resources related to our app.

1. Add the title, "Resources", to the ``<div>`` element with id ``resources-container``. Again, use the ``info-title`` class on the title element.

.. code-block:: html+django
    :emphasize-lines: 2

    <div id="resources-container" class="info-container">
      <h2 class="info-title">Resources</h2>
    </div>

2. Download the following images or find three images of your own and save them to :file:`public/images/`:

  * :download:`coast_80_80.jpg <./resources/coast_80_80.jpg>`
  * :download:`condensation_80_80.jpg <./resources/condensation_80_80.jpg>`
  * :download:`waterfall_80_80.jpg <./resources/waterfall_80_80.jpg>`

.. note::

    In addition to Lorem Ipsum generators, there are also `placeholder image generators <https://loremipsum.io/21-of-the-best-placeholder-image-generators/>`_ that can be used to generate placeholder images for development. Most of these services allow you to specify the size of the images and some of them allow you to specify text that is shown on the image.

3. Add three resources to the ``<div>`` element with id ``resources-container``. Use `Bootstrap Flex Utilities <https://getbootstrap.com/docs/5.2/utilities/flex/#media-object>`_ to create media "objects" for each resource. Each media object includes, a title, a short description and a thumbnail image. The image is wrapped in an ``<a>`` tag that can be used to provide a link to an external resource. Again, use the built-in ``static`` tag to get the paths for the images.

.. code-block:: html+django
    :emphasize-lines: 3-37

    <div id="resources-container" class="info-container">
      <h2 class="info-title">Resources</h2>
      <div class="d-flex align-items-center">
        <div class="flex-shrink-0">
          <a href="#coast">
            <img class="media-object" src="{% static tethys_app|public:'images/coast_80_80.jpg' %}" alt="coast">
          </a>
        </div>
        <div class="media-body flex-grow-1 ms-3">
          <h4 class="media-heading">Lorem Ipsum Dolor</h4>
          Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
        </div>
      </div>

      <div class="d-flex align-items-center mt-2">
        <div class="flex-shrink-0">
          <a href="#condensation">
            <img class="media-object" src="{% static tethys_app|public:'images/condensation_80_80.jpg' %}" alt="condensation">
          </a>
        </div>
        <div class="media-body flex-grow-1 ms-3">
          <h4 class="media-heading">Ut Enim Ad Minim</h4>
          Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.
        </div>
      </div>

      <div class="d-flex align-items-center mt-2">
        <div class="flex-shrink-0">
          <a href="#waterfall">
            <img class="media-object" src="{% static tethys_app|public:'images/waterfall_80_80.jpg' %}" alt="waterfall">
          </a>
        </div>
        <div class="media-body flex-grow-1 ms-3">
          <h4 class="media-heading">Duis Aute Irure</h4>
          Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.
        </div>
      </div>
    </div>

4. Navigate to `<http://localhost:8000/apps/earth-engine/>`_ and verify that the title "Resource" and three media elements with images appear in the panel on the top right. At this point things may look  a bit messy with images overlapping. We'll take care of these issues in a later step. For now, we'll focus on developing the structure of the page.

7. Create Get Started Panel Content
===================================

In this step you will add the content to the Get Started panel. This panel is arguably the most important panel on the home page, as it will provde the "Launch Viewer" button that will link to the viewer page.


1. Add the title, "Get Started", a short paragraph, and a "Launch Viewer" link to the ``<div>`` element with id ``get-started-container``. Again, use the ``info-title`` class on the title element. Use the ``url`` tag with the name of the viewer controller to get the link to the Viewer page:

.. code-block:: html+django
    :emphasize-lines: 2-4

    <div class="info-container">
      <h2 class="info-title">Get Started</h2>
      <p>Press the button below to launch the viewer</p>
      <a id="get-started-btn" href="{% url tethys_app|url:'viewer' %}">Launch Viewer</a>
    </div>

2. Navigate to `<http://localhost:8000/apps/earth-engine/>`_ and verify that the title "Get Started", paragraph, and Launch Viewer link appear in the panel on the bottom right. Click on the Launch Viewer link to verify that it directs the user to the map view page.

8. Customize Style of Home Page
===============================

The Bootstrap CSS framework provides a good base for styling pages in the apps. The home page at this point has the correct 2-column layout that we were after, but it is a fairly bland page and the screenshot image is not contained in it's column. In this step, you'll add a new style sheet for the home page and customize the theme of the home page.

1. Create a new :file:`public/css/home.css` stylesheet.

2. Include the :file:`public/css/home.css` stylesheet in :file:`templates/earth_engine/home.html` by adding the ``styles`` block:

.. code-block:: html+django

    {% block styles %}
      {{ block.super }}
      <link rel="stylesheet" href="{% static tethys_app|public:'css/home.css' %}" />
    {% endblock %}

3. Add the following lines to :file:`public/css/home.css` to customize the appearance of the ``info-container`` panels:

.. code-block:: css

    .info-container {
      background-color: #0000009f;
      box-shadow: 3px 5px 3px rgba(0,0,0,0.35);
      padding: 10px;
      margin-bottom: 30px;
    }

    .info-container .info-title {
      color: #067ef5;
      text-shadow: 2px 2px #000000;
    }

    .info-container p {
      color: #eee;
      text-shadow: 2px 2px #000000;
      font-size: 16px;
    }

    .info-container .media-body {
      color: #eee;
      text-shadow: 2px 2px #000000;
    }

    .info-container .media-object {
      border-radius: 5px;
    }

    .info-container .media-heading {
      color: #eee;
      text-shadow: 2px 2px #000000;
    }

    #feature-image {
      width: 100%;
    }
    
.. note::

    Half of the work of styling the home page has already been done, because the HTML elements of the page contain classes and IDs that make it easy to select and style the elements. Generally, you'll want to use classes to group elements that are styled similarly (e.g.: ``info-container`` classes) and IDs for elements that are unique (e.g.: ``get-started-btn``).

4. Refresh the page to see how the styles change the look and feel of the page. Hard-refresh if necessary (:kbd:`CTRL-SHIFT-R` or :kbd:`CTRL-F5`).

5. Add the following lines to :file:`public/css/home.css` to make the Launch Viewer link appear and behave like a button:

.. code-block:: css

    #get-started-btn {
      display: inline-block;
      border-radius: 15px;
      padding: 5px 10px;
      background-color: #fff;
      color: #044777;
      border: solid 2px rgb(6, 126, 245);
      text-transform: uppercase;
      font-weight: 600;
      align-items: center;
      font-size: 14pt;
      cursor: pointer;
      width: fit-content;
      text-decoration: none !important;
      justify-content: center;
      margin: 10px 0;
    }

    #get-started-btn:hover {
      background-color: #eee;
    }

    #get-started-btn:active,
    #get-started-btn:focus {
      background-color: #044777;
      color: white;
    }

6. Refresh the page to see how the styles change the look and feel of the page. Hard-refresh if necessary (:kbd:`CTRL-SHIFT-R` or :kbd:`CTRL-F5`).

7. Download the :download:`backdrop image <./resources/earth-engine-backdrop.png>` or find your own.

8. Add the following lines to :file:`public/css/home.css` to add a background image to the home page:

.. code-block:: css

    #home-content-container {
      padding: 20px;
      min-height: 100%;
      background: url('/static/earth_engine/images/earth-engine-backdrop.png');
      background-color: #d2dadc;
      background-position: center;
      background-repeat: no-repeat
    }

9. Refresh the page to see how the styles change the look and feel of the page. Hard-refresh if necessary (:kbd:`CTRL-SHIFT-R` or :kbd:`CTRL-F5`).

10. Notice the white space around the border of the page? This is padding in the content area of our base template. To remove the white space so the backdrop image fills the page, add the following lines to :file:`public/css/home.css`:

.. code-block:: css

    #inner-app-content {
      padding: 0;
    }

9. Add a Home Button to Viewer Page
===================================

In this step you will add a Home button to the Viewer page so that users can easily get back to the Home page from the Viewer page.

1. Add a header button to the :file:`templates/earth_engine/viewer.html` template to make it easier to get back to the home page from the viewer page:

.. code-block:: html+django

    {% block header_buttons %}
      <div class="header-button glyphicon-button">
        <a href="{% url tethys_app|url:'home' %}" title="Home"><i class="bi bi-house-door-fill"></i></a>
      </div>
    {% endblock %}

2. Navigate to `<http://localhost:8000/apps/earth-engine/viewer/>`_ and verify that the home button appears in the header and links to the home page.

9. Test and Verify
==================

Browse to `<http://localhost:8000/apps/earth-engine/>`_ in a web browser and login if necessary. Verify the following:

1. The Home page has a background image.
2. The custom styles for the ``info-container`` panels, titles, and Launch Viewer button appear correctly.
3. The Launch Viewer button on the Home page links to the Viewer page.
4. The Home button appears in the header of the Viewer page and links to the Home page.
5. Resize the browser window to different widths. The columns should collapse and stack on top of each other for narrow screens.

10. Solution
============

This concludes this portion of the GEE Tutorial. You can view the solution on GitHub at `<https://github.com/tethysplatform/tethysapp-earth_engine/tree/home-page-solution>`_ or clone it as follows:

.. parsed-literal::

    git clone https://github.com/tethysplatform/tethysapp-earth_engine
    cd tethysapp-earth_engine
    git checkout -b home-page-solution home-page-solution-|version|


