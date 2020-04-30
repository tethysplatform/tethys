***************
Add a Home Page
***************

**Last Updated:** May 2019

In this tutorial you will create a home page for the app with introductory information about that app. This will involve moving the current home page, which contains the map viewer, to a new endpoint and then setting up a new home page view. The following topics will be covered in this tutorial:

* Adding a new view to your app
* Responsive web design using Bootstrap
* Bootstrap Grid System
* Bootstrap Fluid Containers
* Custom styling with CSS
* Linking to other pages and navigation
* Placeholder content for development: lorem ipsum and images

1. Move Map View to Viewer Endpoint
===================================

1. Rename :file:`templates/earth_engine/home.html` to :file:`templates/earth_engine/viewer.html`.

2. Rename ``home`` controller to ``viewer`` in :file:`controllers.py`:

.. code-block:: python

    @login_required()
    @user_workspace
    def viewer(request, user_workspace):
        """
        Controller for the app viewer page.
        """

3. Change the ``render`` call of the ``viewer`` controller to use the new :file:`templates/earth_engine/viewer.html` in :file:`controllers.py`:

.. code-block:: python

    return render(request, 'earth_engine/viewer.html', context)

4. Update the ``UrlMaps`` in :file:`app.py` to the following:

.. code-block:: python

    def url_maps(self):
        """
        Add controllers
        """
        UrlMap = url_map_maker(self.root_url)

        url_maps = (
            UrlMap(
                name='viewer',
                url='earth-engine/viewer',
                controller='earth_engine.controllers.viewer'
            ),
            UrlMap(
                name='get_image_collection',
                url='earth-engine/viewer/get-image-collection',
                controller='earth_engine.controllers.get_image_collection'
            ),
            UrlMap(
                name='get_time_series_plot',
                url='earth-engine/viewer/get-time-series-plot',
                controller='earth_engine.controllers.get_time_series_plot'
            ),
        )

        return url_maps

5. Navigate to `<http://localhost:8000/apps/earth-engine/viewer/>`_ and verify that the map view still functions as it should. Be sure to test loading a dataset or two and plot data at a location.


2. Create New Home Endpoint
===========================

1. Create a new :file:`templates/earth_engine/home.html` with the following contents:

.. code-block:: html+django

    {% extends "earth_engine/base.html" %}
    {% load tethys_gizmos static %}

    {% block app_navigation_items %}
    {% endblock %}

    {% block app_content %}
    {% endblock %}

2. Create a new ``home`` controller in :file:`controllers.py`:

.. code-block:: python

    @login_required()
    def home(request):
        """
        Controller for the app home page.
        """
        context = {}
        return render(request, 'earth_engine/home.html', context)

3. Add a new ``UrlMap`` for the root URL of the app (``earth-engine``) in :file:`app.py`. This new ``UrlMap`` should use the new ``home`` controller:

.. code-block:: python

    def url_maps(self):
        """
        Add controllers
        """
        UrlMap = url_map_maker(self.root_url)

        url_maps = (
            UrlMap(
                name='home',
                url='earth-engine',
                controller='earth_engine.controllers.home'
            ),
            UrlMap(
                name='viewer',
                url='earth-engine/viewer',
                controller='earth_engine.controllers.viewer'
            ),
            UrlMap(
                name='get_image_collection',
                url='earth-engine/viewer/get-image-collection',
                controller='earth_engine.controllers.get_image_collection'
            ),
            UrlMap(
                name='get_time_series_plot',
                url='earth-engine/viewer/get-time-series-plot',
                controller='earth_engine.controllers.get_time_series_plot'
            ),
            UrlMap(
                name='about',
                url='earth-engine/about',
                controller='earth_engine.controllers.about'
            ),
        )

        return url_maps

4. Navigate to `<http://localhost:8000/apps/earth-engine/>`_ and verify that the new home page is functioning properly (the page should be blank).

3. Remove Navigation from Home Page
===================================

1. Replace the ``app_navigation_items`` block with the ``app_navigation_override`` block in :file:`templates/earth_engine/home.html` to remove the navigation panel from the home page:

.. code-block:: html+django

    {% block app_navigation_override %}
    {% endblock %}

2. Create a new :file:`public/css/no_nav.css` style sheet with styles to adjust the header appropriately when there is no navigation toggle button in the header:

.. code-block:: css

    #nav-title-wrapper {
      margin-left: 15px;
    }

    #app-content-wrapper #app-content {
      height: 100%;
    }

    #app-content-wrapper.show-nav #app-content {
      padding-right: 0;
      transform: none;
    }

    #inner-app-content {
      padding: 0;
    }

3. Include the :file:`public/css/no_nav.css` stylesheet in :file:`templates/earth_engine/home.html`:

.. code-block:: html+django

    {% block styles %}
      {{ block.super }}
      <link rel="stylesheet" href="{% static 'earth_engine/css/no_nav.css' %}" />
    {% endblock %}

4. Navigate to `<http://localhost:8000/apps/earth-engine/>`_ and verify that the app icon in the header has spacing on the left.

4. Layout Home Page Grid with Bootstrap
=======================================

Create a responsive two column layout using the `Bootstrap Grid System <https://getbootstrap.com/docs/3.3/css/#grid>`_.

1. First create a ``<div>`` element with class ``container-fluid``:

.. code-block:: html+django
    :emphasize-lines: 2-3

    {% block app_content %}
    <div  id="home-content-container" class="container-fluid">
    </div>
    {% endblock %}

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

6. TODO: Verify with CSS?


5. Create About Panel Content
=============================

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

    <div class="info-container">
      <h2 id="about-container" class="info-title">About</h2>
      <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Eget est lorem ipsum dolor sit amet. Morbi tincidunt augue interdum velit euismod in pellentesque.</p>
      <p>Ac felis donec et odio pellentesque. Quis ipsum suspendisse ultrices gravida dictum fusce ut. Curabitur gravida arcu ac tortor dignissim convallis aenean et tortor. Sed euismod nisi porta lorem mollis. Nisi scelerisque eu ultrices vitae. Sit amet consectetur adipiscing elit duis. At in tellus integer feugiat scelerisque varius morbi enim.</p>
      <img id="feature-image" src="{% static 'earth_engine/images/earth-engine-viewer.png' %}">
    </div>

4. Navigate to `<http://localhost:8000/apps/earth-engine/>`_ and verify that the title "About", filler paragraphs, and screenshot appear in the panel on the left.


6. Create Resources Panel Content
=================================

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

3. Add three resources to the ``<div>`` element with id ``resources-container``. Use `Boostrap Media Objects <https://getbootstrap.com/docs/3.3/components/#media>`_ to style each resource. Each media object/resource includes, a title, a short description and a thumbnail image. The image is wrapped in an ``<a>`` tag that can be used to provide a link to an external resource. Again, use the built-in ``static`` tag to get the paths for the images.

.. code-block:: html+django
    :emphasize-lines: 3-37

    <div id="resources-container" class="info-container">
      <h2 class="info-title">Resources</h2>
      <div class="media">
        <div class="media-left">
          <a href="#coast">
            <img class="media-object" src="{% static 'earth_engine/images/coast_80_80.jpg' %}" alt="">
          </a>
        </div>
        <div class="media-body">
          <h4 class="media-heading">Lorem Ipsum Dolor</h4>
          Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
        </div>
      </div>

      <div class="media">
        <div class="media-left">
          <a href="#condensation">
            <img class="media-object" src="{% static 'earth_engine/images/condensation_80_80.jpg' %}" alt="">
          </a>
        </div>
        <div class="media-body">
          <h4 class="media-heading">Ut Enim Ad Minim</h4>
          Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.
        </div>
      </div>

      <div class="media">
        <div class="media-left">
          <a href="#waterfall">
            <img class="media-object" src="{% static 'earth_engine/images/waterfall_80_80.jpg' %}" alt="">
          </a>
        </div>
        <div class="media-body">
          <h4 class="media-heading">Duis Aute Irure</h4>
          Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.
        </div>
      </div>
    </div>

4. Navigate to `<http://localhost:8000/apps/earth-engine/>`_ and verify that the title "Resource" and three media elements with images appear in the panel on the top right.

7. Create Get Started Panel Content
===================================

1. Add the title, "Get Started", a short paragraph, and a "Launch Viewer" link to the ``<div>`` element with id ``get-started-container``. Again, use the ``info-title`` class on the title element. Use the ``url`` tag with the name of the viewer controller to get the link to the Viewer page:

.. code-block:: html+django
    :emphasize-lines: 2-4

    <div class="info-container">
      <h2 class="info-title">Get Started</h2>
      <p>Press the button below to launch the viewer</p>
      <a id="get-started-btn" href="{% url 'earth_engine:viewer' %}">Launch Viewer</a>
    </div>

2. Navigate to `<http://localhost:8000/apps/earth-engine/>`_ and verify that the title "Get Started", paragraph, and Launch Viewer link appear in the panel on the bottom right. Click on the Launch Viewer link to verify that it directs the user to the map view page.

8. Customize Style of Home Page
===============================

1. Create a new :file:`public/css/home.css` stylesheet.

2. Include the :file:`public/css/home.css` stylesheet in :file:`templates/earth_engine/home.html`:

.. code-block:: html+django
    :emphasize-lines: 4

    {% block styles %}
      {{ block.super }}
      <link rel="stylesheet" href="{% static 'earth_engine/css/no_nav.css' %}" />
      <link rel="stylesheet" href="{% static 'earth_engine/css/home.css' %}" />
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

9. Add a Home Button to Viewer Page
===================================

1. Add a header button to the :file:`templates/earth_engine/viewer.html` template to make it easier to get back to the home page from the viewer page:

.. code-block:: html+django

    {% block header_buttons %}
      <div class="header-button glyphicon-button">
        <a href="{% url 'earth_engine:home' %}" title="Home"><span class="glyphicon glyphicon-home"></span></a>
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

This concludes this portion of the GEE Tutorial. You can view the solution on GitHub at `<https://github.com/tethysplatform/tethysapp-earth_engine/tree/home-page-solution-3.0>`_ or clone it as follows:

.. parsed-literal::

    git clone https://github.com/tethysplatform/tethysapp-earth_engine.git
    cd tethysapp-earth_engine
    git checkout -b home-page-solution home-page-solution-|version|


