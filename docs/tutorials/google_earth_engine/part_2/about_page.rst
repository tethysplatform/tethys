***********************************
Add About Page and Disclaimer Modal
***********************************

**Last Updated:** May 2020

In this tutorial you will add an About page and a disclaimer modal. The requirements for the About page include a fixed width content area, two columns with text on the left and images on the right, and a list of sponsor logos at the bottom. The Disclaimer modal needs to be available from any page in the app and should also include the sponsor logos. Topics that will be covered in this tutorial include:

* Adding a new view to your app
* Responsive web design using Bootstrap
* Bootstrap Grid System
* Bootstrap Non-Fluid or Fixed Containers
* Bootstrap Modals
* Custom styling with CSS
* Linking to other pages and navigation
* Placeholder content for development: lorem ipsum and images

0. Start From Previous Solution (Optional)
==========================================

If you wish to use the previous solution as a starting point:

.. parsed-literal::

    git clone https://github.com/tethysplatform/tethysapp-earth_engine.git
    cd tethysapp-earth_engine
    git checkout -b home-page-solution home-page-solution-|version|

1. Create new Template, Controller, and UrlMap for About Page
=============================================================

1. Create new :file:`templates/earth_engine/about.html` template:

.. code-block:: html+django

    {% extends "earth_engine/base.html" %}
    {% load static %}

    {% block app_navigation_override %}
    {% endblock %}

    {% block app_content %}
    <h1>This is the About Page</h1>
    {% endblock %}

2. Create new ``about`` controller in :file:`controllers.py`:

.. code-block:: python

    @login_required()
    def about(request):
        """
        Controller for the app about page.
        """
        context = {}
        return render(request, 'earth_engine/about.html', context)

3. Create new ``UrlMap`` in :file:`app.py` for the ``about`` controller:

.. code-block:: python
    :emphasize-lines: 28-32

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
                )
            )

            return url_maps

4. Navigate to `<http://localhost:8000/apps/earth-engine/about/>`_ and verify that the new page loads. You should see the "This is the About Page" text.

2. Modify Header Buttons to Navigate between About Page and Home Page
=====================================================================

1. Move Home header button from :file:`templates/earth_engine/viewer.html` to :file:`templates/earth_engine/base.html` so it is available on all pages:

.. code-block:: html+django

    {% block header_buttons %}
      <div class="header-button glyphicon-button">
        <a href="{% url 'earth_engine:home' %}" title="Home"><span class="glyphicon glyphicon-home"></span></a>
      </div>
    {% endblock %}

.. important::

    Be sure to delete these lines in :file:`templates/earth_engine/viewer.html`.

2. Create new About header button in :file:`templates/earth_engine/base.html`:

.. code-block:: html+django
    :emphasize-lines: 5-7

    {% block header_buttons %}
      <div class="header-button glyphicon-button">
        <a href="{% url 'earth_engine:home' %}" title="Home"><span class="glyphicon glyphicon-home"></span></a>
      </div>
      <div class="header-button glyphicon-button">
        <a href="{% url 'earth_engine:about' %}" title="About"><span class="glyphicon glyphicon-info-sign"></span></a>
      </div>
    {% endblock %}

3. Navigate to `<http://localhost:8000/apps/earth-engine/about/>`_ and verify that the Home and About buttons in the header function as expected. Also navigate to the viewer page and verify that the Home and About buttons appear on that page as well.

3. Build out About Page
=======================

1. Create a ``<div>`` element with class ``container`` in the ``app_content`` block:

.. code-block:: html+django
    :emphasize-lines: 2-3

    {% block app_content %}
      <div class="container">
      </div>
    {% endblock %}

2. Create a ``<div>`` element with class ``page-header`` and the following contents inside the ``container`` ``<div>``:

.. code-block:: html+django
    :emphasize-lines: 3-6

    {% block app_content %}
      <div class="container">
        <div class="page-header">
          <h1>About Earth Engine</h1>
          <h1><small>Sit Amet Consectetur Adipiscing</small></h1>
        </div>
      </div>
    {% endblock %}

3. Add two ``<div>`` elements with class ``row``:

.. code-block:: html+django
    :emphasize-lines: 7-10

    {% block app_content %}
      <div class="container">
        <div class="page-header">
          <h1>About Earth Engine</h1>
          <h1><small>Sit Amet Consectetur Adipiscing</small></h1>
        </div>
        <div class="row">
        </div>
        <div class="row">
        </div>
      </div>
    {% endblock %}

4. The upper ``row`` should have two columns for the About page content. The bottom row should have a single full-width column that will contain the sponsor logos. Add column ``<div>`` elements to each ``row`` ``<div>`` as follows:

.. code-block:: html+django
    :emphasize-lines: 2-9, 12-13

    <div class="row">
      <!-- Left Column -->
      <div class="col-md-8">
      </div>
      <!-- End Left Column -->
      <!-- Right Column -->
      <div class="col-md-4">
      </div>
      <!-- End Right Column -->
    </div>
    <div class="row">
      <div class="col-md-12">
      </div>
    </div>

5. It is helpful to use placeholder text and images while you are developing a website (lorem ipsum). Add the following placeholder content to the columns in the **first** ``row``:

.. code-block:: html+django
    :emphasize-lines: 4-11, 16-20

    <div class="row">
      <!-- Left Column -->
      <div class="col-md-8">
        <div class="about-content">
          <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Euismod nisi porta lorem mollis. Congue quisque egestas diam in arcu cursus euismod. Auctor neque vitae tempus quam pellentesque nec nam. Erat imperdiet sed euismod nisi porta lorem. Nunc eget lorem dolor sed viverra ipsum nunc aliquet bibendum. Sed blandit libero volutpat sed cras ornare. Convallis tellus id interdum velit laoreet id. Amet mauris commodo quis imperdiet massa tincidunt. Mi bibendum neque egestas congue quisque egestas diam in. Enim nec dui nunc mattis enim ut tellus elementum sagittis. Cursus mattis molestie a iaculis at erat pellentesque. Ut tellus elementum sagittis vitae et leo.</p>
          <h6>Eu Consequat ac Felis</h6>
          <p>Eu consequat ac felis donec et odio. Eget arcu dictum varius duis at consectetur lorem. Lorem ipsum dolor sit amet consectetur. Turpis egestas integer eget aliquet nibh praesent. Mattis rhoncus urna neque viverra justo nec. Iaculis urna id volutpat lacus laoreet non curabitur gravida arcu. Convallis posuere morbi leo urna molestie at elementum eu. Fermentum et sollicitudin ac orci phasellus egestas tellus. Convallis aenean et tortor at risus. Morbi tristique senectus et netus et malesuada fames ac. Sed vulputate mi sit amet mauris commodo quis. Nisi quis eleifend quam adipiscing vitae proin sagittis nisl. Id venenatis a condimentum vitae sapien pellentesque habitant morbi tristique. Id cursus metus aliquam eleifend mi in nulla. Proin fermentum leo vel orci porta non pulvinar neque laoreet. Lobortis mattis aliquam faucibus purus in massa tempor. Varius vel pharetra vel turpis nunc.</p>
          <p><b>Mauris rhoncus aenean vel elit:</b> Blandit aliquam etiam erat velit. Auctor neque vitae tempus quam pellentesque nec nam. Augue mauris augue neque gravida in fermentum et. Tempus urna et pharetra pharetra. Vel turpis nunc eget lorem. Vitae nunc sed velit dignissim. Enim tortor at auctor urna nunc id. Pellentesque habitant morbi tristique senectus et netus et. Tellus integer feugiat scelerisque varius morbi enim nunc faucibus.</p>
          <p><b>Blandit turpis cursus in hac habitasse platea:</b> Tellus elementum sagittis vitae et leo duis ut diam quam. Amet nisl purus in mollis nunc sed. Ac feugiat sed lectus vestibulum. Suscipit adipiscing bibendum est ultricies integer quis. Tortor pretium viverra suspendisse potenti nullam ac tortor. Blandit turpis cursus in hac. Id porta nibh venenatis cras sed felis eget velit. Fermentum posuere urna nec tincidunt praesent semper feugiat nibh sed. Pellentesque elit ullamcorper dignissim cras tincidunt lobortis feugiat vivamus at. Sapien et ligula ullamcorper malesuada proin libero nunc consequat. Aliquet enim tortor at auctor urna nunc id. Fringilla ut morbi tincidunt augue interdum velit euismod in. In arcu cursus euismod quis viverra nibh. Vulputate ut pharetra sit amet. Purus in massa tempor nec. Pellentesque massa placerat duis ultricies lacus sed. Integer feugiat scelerisque varius morbi enim. Vitae tempus quam pellentesque nec nam.</p>
          <p><b>Sed cras ornare arcu dui vivamus arcu:</b> Pellentesque adipiscing commodo elit at. Fusce id velit ut tortor pretium viverra. Nunc vel risus commodo viverra. Dui faucibus in ornare quam viverra orci sagittis eu volutpat. Aliquet nibh praesent tristique magna. Purus sit amet volutpat consequat. Gravida neque convallis a cras. Aenean euismod elementum nisi quis eleifend. At tellus at urna condimentum mattis pellentesque id nibh tortor. Sit amet massa vitae tortor. Volutpat lacus laoreet non curabitur gravida arcu ac. Vulputate dignissim suspendisse in est ante. Tempor commodo ullamcorper a lacus vestibulum. Quis vel eros donec ac odio tempor. Lacus sed turpis tincidunt id aliquet risus feugiat in ante. Metus aliquam eleifend mi in.</p>'
        </div>
      </div>
      <!-- End Left Column -->
      <!-- Right Column -->
      <div class="col-md-4">
        <div class="about-imgs">
          <img class="about-img" src="http://placeimg.com/360/200/nature">
          <img class="about-img" src="http://placeimg.com/360/250/nature">
          <img class="about-img" src="http://placeimg.com/360/300/nature">
        </div>
      </div>
      <!-- End Right Column -->
    </div>

6. Add the following content to the column in the **second** ``row``:

.. code-block:: html+django
    :emphasize-lines: 3-12

    <div class="row">
      <div class="col-md-12">
        <div class="about-footer-content">
          <h3>Sponsors</h3>
          <img src="https://via.placeholder.com/50/0000ff/000000?text=1">
          <img src="https://via.placeholder.com/50/00ff00/000000?text=2">
          <img src="https://via.placeholder.com/50/ff0000/000000?text=3">
          <img src="https://via.placeholder.com/50/00ffff/000000?text=4">
          <img src="https://via.placeholder.com/50/ffff00/000000?text=5">
          <img src="https://via.placeholder.com/50/ff8800/000000?text=6">
          <img src="https://via.placeholder.com/50/8800ff/000000?text=7">
        </div>
      </div>
    </div>

7. Navigate to `<http://localhost:8000/apps/earth-engine/about/>`_ and verify that the content renders as expected. Resize the window to see how the normal Bootstrap ``container`` differs from the ``container-fluid`` that was used on the home page.

4. Customize the About Page Styles
==================================

1. Create a new :file:`public/earth_engine/about.css` stylesheet.

2. Include the new :file:`about.css` as well as the :file:`no_nav.css` stylesheets in :file:`templates/earth_engine/about.html`:

.. code-block:: html+django

    {% block styles %}
      {{ block.super }}
      <link rel="stylesheet" href="{% static 'earth_engine/css/no_nav.css' %}" />
      <link rel="stylesheet" href="{% static 'earth_engine/css/about.css' %}" />
    {% endblock %}

3. Add the following contents to :file:`public/earth_engine/about.css` to customize the style of the page header:

.. code-block:: css

    .page-header h1 {
      text-align: center;
      font-size: 48pt;
      color: black;
    }

4. Navigate to `<http://localhost:8000/apps/earth-engine/about/>`_ and verify that the header is centered on the page and in a larger font. Hard-refresh the page if necessary (:kbd:`CTRL-SHIFT-R` or :kbd:`CTRL-F5`).

5. Add the following contents to :file:`public/earth_engine/about.css` to style the images to fit in their column in the About page content:

.. code-block:: css

    .about-img {
      width: 100%;
      max-width: 360px;
      margin-bottom: 20px;
    }

6. Navigate to `<http://localhost:8000/apps/earth-engine/about/>`_ and verify the images fit within the column appropriately. Hard-refresh the page if necessary (:kbd:`CTRL-SHIFT-R` or :kbd:`CTRL-F5`).

7. Add the following contents to :file:`public/earth_engine/about.css` to style the footer of the About page:

.. code-block:: css

    .about-footer-content {
      text-align: center;
      margin: 50px 0 100px 0;
    }

    .about-footer-content h3 {
      margin-bottom: 26px;
    }

    .about-footer-content img {
      margin: 0 5px;
    }

8. Navigate to `<http://localhost:8000/apps/earth-engine/about/>`_ and verify that the sponsor images are centered. Hard-refresh the page if necessary (:kbd:`CTRL-SHIFT-R` or :kbd:`CTRL-F5`).

5. Create the Disclaimer Modal
==============================

1. Create a new Bootstrap modal in :file:`templates/earth_engine/base.html`. Modals should be placed in the ``after_app_content`` block:

.. code-block:: html+django

    {# Use the after_app_content block for modals #}
    {% block after_app_content %}
      {{ block.super }}
      <!-- Info Modal -->
      <div class="modal fade" id="disclaimer-modal" tabindex="-1" role="dialog" aria-labelledby="disclaimer-modal-label">
        <div class="modal-dialog" role="document">
          <div class="modal-content">
            <div class="modal-header">
              <button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button>
              <h2 class="modal-title" id="disclaimer-modal-label">Disclaimer</h2>
            </div>
            <div class="modal-body">
            </div>
            <div class="modal-footer">
            </div>
          </div>
        </div>
      </div>
      <!-- End Info Modal -->
    {% endblock %}

2. Add a header button to launch the modal in :file:`templates/earth_engine/base.html`:

.. code-block:: html+django
    :emphasize-lines: 9-11

    {% block header_buttons %}
      {{ block.super }}
      <div class="header-button glyphicon-button">
        <a href="{% url 'earth_engine:home' %}" title="Home"><span class="glyphicon glyphicon-home"></span></a>
      </div>
      <div class="header-button glyphicon-button">
        <a href="{% url 'earth_engine:about' %}" title="About"><span class="glyphicon glyphicon-info-sign"></span></a>
      </div>
      <div class="header-button glyphicon-button">
        <a data-toggle="modal" data-target="#disclaimer-modal" title="Disclaimer"><span class="glyphicon glyphicon-warning-sign"></span></a>
      </div>
    {% endblock %}

3. Navigate to `<http://localhost:8000/apps/earth-engine/about/>`_ and verify that the modal opens when the Disclaimer header button is pressed. Also verify that the Disclaimer button is on every page of the app.

4. Add the following content to the ``modal-body`` ``<div>`` element in :file:`templates/earth_engine/base.html`:

.. code-block:: html+django

    <div class="modal-body">
      <div id="disclaimer-container">
        <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Pellentesque sed ipsum mollis, congue metus vitae, fringilla tortor. Cras non magna tempus, pretium nibh a, accumsan sapien. Quisque quis diam justo. Mauris ut diam molestie, scelerisque nibh ac, convallis mauris. Sed risus ex, blandit eu lectus vitae, vulputate fermentum metus. Class aptent taciti sociosqu ad litora torquent per conubia nostra, per inceptos himenaeos. Integer pretium sagittis arcu at aliquet. Quisque quis sodales urna. Suspendisse nisl odio, facilisis ac iaculis quis, accumsan non justo. Nunc eu porttitor neque.</p>
        <p>Sed vel nisl leo. Quisque venenatis erat nec erat laoreet, ac vulputate magna sodales. Ut in enim finibus, finibus orci sit amet, feugiat erat. Vivamus id lorem arcu. Integer lacus lorem, rhoncus vitae elit eu, vestibulum placerat nibh. Ut eget lectus in quam blandit molestie nec et leo. Ut augue libero, commodo id ligula sit amet, placerat molestie enim. Cras justo odio, vulputate id odio non, ultricies mollis sem. Integer et vestibulum erat, eu dictum nunc. Donec eu diam ac ligula aliquam egestas in non lectus. Nullam quis arcu eget massa feugiat sollicitudin. Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas. Nulla quis urna efficitur, sagittis ante eget, accumsan nulla.</p>
        <p>Pellentesque tempor neque in odio ullamcorper, a varius lectus euismod. Donec odio nunc, mollis aliquam imperdiet eget, lacinia sit amet dui. Morbi quis pellentesque lorem. Nam volutpat vestibulum ex vel interdum. Etiam accumsan luctus felis gravida sodales. Praesent malesuada lectus tortor, at maximus velit fringilla sed. Ut consequat nisl ut pretium egestas.</p>
        <p>Quisque tincidunt ex a sem sagittis molestie. Nunc pellentesque et tortor quis lobortis. Etiam eget justo risus. Nunc a lobortis quam, id varius ante. Maecenas at rhoncus enim. Maecenas aliquam non elit quis tempor. Morbi eu ligula imperdiet, imperdiet neque non, faucibus eros. Vivamus ac sollicitudin nunc. Vivamus sagittis ut orci eu auctor. Nulla sit amet facilisis felis, eu tincidunt sapien. Nulla sit amet dignissim nisi. Cras pellentesque rutrum rhoncus. Nulla nibh erat, congue sit amet feugiat in, eleifend at massa. Maecenas risus massa, placerat non velit vel, laoreet cursus nunc.</p>
        <p>Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas. Nam ultricies accumsan elit vel volutpat. Proin nec nibh ac dolor tempor sollicitudin. Praesent nisi elit, placerat eget diam nec, viverra euismod felis. Nunc accumsan nulla non eros bibendum, mollis hendrerit enim cursus. In ex lorem, hendrerit ut nibh nec, vestibulum placerat massa. Proin at odio non nisl eleifend venenatis ut at tortor.</p>
      </div>
    </div>

5. Add the following content to the ``modal-footer`` ``<div>`` element in :file:`templates/earth_engine/base.html`:

.. code-block:: html+django

    <div class="modal-footer">
      <div id="sponsors-container">
        <h6>Sponsors:</h6>
        <img src="https://via.placeholder.com/50/0000ff/000000?text=1">
        <img src="https://via.placeholder.com/50/00ff00/000000?text=2">
        <img src="https://via.placeholder.com/50/ff0000/000000?text=3">
        <img src="https://via.placeholder.com/50/00ffff/000000?text=4">
        <img src="https://via.placeholder.com/50/ffff00/000000?text=5">
        <img src="https://via.placeholder.com/50/ff8800/000000?text=6">
        <img src="https://via.placeholder.com/50/8800ff/000000?text=7">
      </div>
    </div>

6. Navigate to `<http://localhost:8000/apps/earth-engine/about/>`_ and verify that new content appears in the disclaimer modal.

6. Customize the Disclaimer Modal Styles
========================================

1. Create a new :file:`public/earth_engine/disclaimer_modal.css` stylesheet with the following contents:

.. code-block:: css

    #disclaimer-container {
      height: 400px;
      overflow-y: auto;
    }

    #sponsors-container {
      text-align: left;
    }

    #sponsors-container img {
      height: 50px;
      width: 50px;
      margin-right: 10px;
      border-radius: 5px;
    }

    #sponsors-container h6 {
        display: inline-block;
        margin-right: 10px;
    }

2. Include the new stylesheet in :file:`templates/earth_engine/base.html`:

.. code-block:: html+django
    :emphasize-lines: 4

    {% block content_dependent_styles %}
      {{ block.super }}
      <link href="{% static 'earth_engine/css/main.css' %}" rel="stylesheet"/>
      <link href="{% static 'earth_engine/css/disclaimer_modal.css' %}" rel="stylesheet"/>
    {% endblock %}

3. Navigate to `<http://localhost:8000/apps/earth-engine/about/>`_ and verify the style changes worked. Hard-refresh the page if necessary (:kbd:`CTRL-SHIFT-R` or :kbd:`CTRL-F5`). Open the Disclaimer modal on the other pages of the app to verify that the modal looks the same on all pages.

7. Solution
===========

This concludes this portion of the GEE Tutorial. You can view the solution on GitHub at `<https://github.com/tethysplatform/tethysapp-earth_engine/tree/about-page-solution-3.0>`_ or clone it as follows:

.. parsed-literal::

    git clone https://github.com/tethysplatform/tethysapp-earth_engine.git
    cd tethysapp-earth_engine
    git checkout -b about-page-solution about-page-solution-|version|