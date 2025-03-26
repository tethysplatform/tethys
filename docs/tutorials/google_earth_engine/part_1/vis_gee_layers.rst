**************************************
Visualize Google Earth Engine Datasets
**************************************

**Last Updated:** July 2024

In this tutorial you will load the GEE dataset the user has selected into the map view. The following topics will be reviewed in this tutorial:

* Tethys MapView Gizmo JavaScript API
* JQuery AJAX Calls
* Authenticating with GEE in Tethys Apps
* Retrieving GEE XYZ Tile Layer Endpoints
* Logging in Tethys

.. figure:: ../../../images/tutorial/gee/visualize_gee_layers.png
    :width: 800px
    :align: center

0. Start From Previous Solution (Optional)
==========================================

If you wish to use the previous solution as a starting point:

.. parsed-literal::

    git clone https://github.com/tethysplatform/tethysapp-earth_engine
    cd tethysapp-earth_engine
    git checkout -b map-view-solution map-view-solution-|version|

.. _gee_authentication_step:

1. Handle GEE Authentication
============================

To use GEE services, your app will need to authenticate using a GEE Account. This step will illustrate *one* way that this can be handled.

1. Create a new Python module in the :file:`gee` package called :file:`params.py` with the following contents:

.. code-block:: python

    service_account = ''  # your google service account
    private_key = ''  # path to the json private key for the service account

2. Create a new Python module in the :file:`gee` package called :file:`methods.py` with the following contents:

.. code-block:: python

    import logging
    import ee
    from ee.ee_exception import EEException
    from . import params as gee_account
    from .products import EE_PRODUCTS
    from . import cloud_mask as cm

    log = logging.getLogger(f'tethys.apps.{__name__}')

    if gee_account.service_account:
        try:
            credentials = ee.ServiceAccountCredentials(gee_account.service_account, gee_account.private_key)
            ee.Initialize(credentials)
        except EEException as e:
            print(str(e))
    else:
        try:
            ee.Initialize()
        except EEException as e:
            log.warning('Unable to initialize GEE. If installing ignore this warning.')
            

    def image_to_map_id(image_name, vis_params={}):
        """
        Get map_id parameters
        """
        pass


    def get_image_collection_asset(platform, sensor, product, date_from=None, date_to=None, reducer='median'):
        """
        Get tile url for image collection asset.
        """
        pass

.. important::

    The code at the top of this module handles authenticating with Google Earth Engine automatically when it is imported. By default it will check the ``params.py`` module for service account credentials and then fall back to checking the credentials file you generated earlier (see: :ref:`authenticate_gee_locally` of :doc:`./gee_primer`). Authenticating using the credential file works well for development but it will not work when you deploy the app. For production you will need to obtain and use a `Google Earth Engine Service Account <https://developers.google.com/earth-engine/guides/service_account>`_. Then add the credentials to the ``gee.param.py`` module. **DO NOT COMMIT THESE CREDENTIALS IN A PUBLIC REPOSITORY**.

2. Implement GEE Methods
========================

Google Earth Engine provides XYZ tile services for each of their datasets. In this step, you'll write the necessary GEE logic to retrieve a tile service endpoint for a given dataset product.

1. Some of the datasets require functions for filtering out the clouds in the images, so you'll create a module with functions for removing the clouds. Create a new Python module in the :file:`gee` package called :file:`cloud_mask.py` with the following contents:

.. code-block:: python

    import ee


    def mask_l8_sr(image):
        """
        Cloud Mask for Landsat 8 surface reflectance. Derived From: https://developers.google.com/earth-engine/datasets/catalog/LANDSAT_LC08_C01_T1_SR
        """
        # Bits 3 and 5 are cloud shadow and cloud, respectively.
        cloudShadowBitMask = (1 << 3)
        cloudsBitMask = (1 << 5)

        # Get the pixel QA band.
        qa = image.select('pixel_qa')

        # Both flags should be set to zero, indicating clear conditions.
        mask = qa.bitwiseAnd(cloudShadowBitMask).eq(0).And(qa.bitwiseAnd(cloudsBitMask).eq(0))
        return image.updateMask(mask)


    def cloud_mask_l457(image):
        """
        Cloud Mask for Landsat 7 surface reflectance. Derived From: https://developers.google.com/earth-engine/datasets/catalog/LANDSAT_LE07_C01_T1_SR
        """
        qa = image.select('pixel_qa')

        # If the cloud bit (5) is set and the cloud confidence (7) is high
        # or the cloud shadow bit is set (3), then it's a bad pixel.
        cloud = qa.bitwiseAnd(1 << 5).And(qa.bitwiseAnd(1 << 7)).Or(qa.bitwiseAnd(1 << 3))

        # Remove edge pixels that don't occur in all bands
        mask2 = image.mask().reduce(ee.Reducer.min())

        return image.updateMask(cloud.Not()).updateMask(mask2)


    def mask_s2_clouds(image):
        """
        Cloud Mask for Sentinel 2 surface reflectance. Derived from: https://developers.google.com/earth-engine/datasets/catalog/COPERNICUS_S2
        """
        qa = image.select('QA60')

        # Bits 10 and 11 are clouds and cirrus, respectively.
        cloudBitMask = 1 << 10
        cirrusBitMask = 1 << 11

        # Both flags should be set to zero, indicating clear conditions.
        mask = qa.bitwiseAnd(cloudBitMask).eq(0).And(qa.bitwiseAnd(cirrusBitMask).eq(0))

        return image.updateMask(mask).divide(10000)

2. The ``get_image_collection_asset`` function builds the map tile service URL for the given platform, sensor, and product and filters it by the dates and reducer method. Implement the ``get_image_collection_asset`` function as follows in :file:`methods.py`:

.. code-block:: python

    def get_image_collection_asset(platform, sensor, product, date_from=None, date_to=None, reducer='median'):
        """
        Get tile url for image collection asset.
        """
        ee_product = EE_PRODUCTS[platform][sensor][product]

        collection = ee_product['collection']
        index = ee_product.get('index', None)
        vis_params = ee_product.get('vis_params', {})
        cloud_mask = ee_product.get('cloud_mask', None)

        log.debug(f'Image Collection Name: {collection}')
        log.debug(f'Band Selector: {index}')
        log.debug(f'Vis Params: {vis_params}')

        try:
            ee_collection = ee.ImageCollection(collection)

            if date_from and date_to:
                ee_filter_date = ee.Filter.date(date_from, date_to)
                ee_collection = ee_collection.filter(ee_filter_date)

            if index:
                ee_collection = ee_collection.select(index)

            if cloud_mask:
                cloud_mask_func = getattr(cm, cloud_mask, None)
                if cloud_mask_func:
                    ee_collection = ee_collection.map(cloud_mask_func)

            if reducer:
                ee_collection = getattr(ee_collection, reducer)()

            tile_url = image_to_map_id(ee_collection, vis_params)

            return tile_url

        except EEException:
            log.exception('An error occurred while attempting to retrieve the image collection asset.')

3. Implement the ``image_to_map_id`` function as follows in :file:`methods.py`:

.. code-block:: python

    def image_to_map_id(image_name, vis_params={}):
        """
        Get map_id parameters
        """
        try:
            ee_image = ee.Image(image_name)
            map_id = ee_image.getMapId(vis_params)
            tile_url = map_id['tile_fetcher'].url_format
            return tile_url

        except EEException:
            log.exception('An error occurred while attempting to retrieve the map id.')

3. Create Endpoint for Getting Map Images
=========================================

In this step you'll create a new endpoint that can be used to call the ``get_image_collection_asset`` function from the client-side of the application.

1. Add a new controller called ``get_image_collection`` to :file:`controllers.py`:

.. code-block:: python

    import logging
    from django.http import JsonResponse, HttpResponseNotAllowed
    from .gee.methods import get_image_collection_asset

    log = logging.getLogger(f'tethys.apps.{__name__}')

.. code-block:: python

    @controller
    def get_image_collection(request):
        """
        Controller to handle image collection requests.
        """
        response_data = {'success': False}

        if request.method != 'POST':
            return HttpResponseNotAllowed(['POST'])

        try:
            log.debug(f'POST: {request.POST}')

            platform = request.POST.get('platform', None)
            sensor = request.POST.get('sensor', None)
            product = request.POST.get('product', None)
            start_date = request.POST.get('start_date', None)
            end_date = request.POST.get('end_date', None)
            reducer = request.POST.get('reducer', None)

            url = get_image_collection_asset(
                platform=platform,
                sensor=sensor,
                product=product,
                date_from=start_date,
                date_to=end_date,
                reducer=reducer
            )

            log.debug(f'Image Collection URL: {url}')

            response_data.update({
                'success': True,
                'url': url
            })

        except Exception as e:
            response_data['error'] = f'Error Processing Request: {e}'

        return JsonResponse(response_data)

.. tip::

    In this step you added ``logging`` to the new endpoint. Tethys and Django leverage Python's built-in logging capabilities. Use logging statements in your code to provide useful debugging information, system status, or error capture in your production logs. The logging for a portal can be configured in the :ref:`tethys_configuration`. To learn more about logging in Tethys/Django see: `Django Logging <https://docs.djangoproject.com/en/2.2/topics/logging/>`_

4. Stub Out the Map JavaScript Methods
======================================

In this step you'll stub out the methods and variables you'll need to add the GEE layers to the map.

1. Add the following new variables to the *MODULE LEVEL / GLOBAL VARIABLES* section of :file:`public/js/gee_datasets.js`:

.. code-block:: javascript

    // Map Variables
    var m_map,
    m_gee_layer;

.. note::

    The prepending an **m** to these variables is a reminder that they are module level variables.

2. Add the following module function declarations to the *PRIVATE FUNCTION DECLARATIONS* section of :file:`public/js/gee_datasets.js`:

.. code-block:: javascript

    // Map Methods
    var update_map, update_data_layer, create_data_layer, clear_map;

3. Add the following module function stubs to the *PRIVATE FUNCTION IMPLEMENTATIONS* section of :file:`public/js/gee_datasets.js`, just below the ``collect_data`` method:

.. code-block:: javascript

    // Map Methods
    update_map = function() {};

    update_data_layer = function(url) {};

    create_data_layer = function(url) {};

    clear_map = function() {};

.. note::

    The lines that define empty functions (e.g.: ``update_map = function() {};``) are method stubs that will be implemented in future steps.

4. Use the Tethys ``MapView`` JavaScript API to retrieve the underlying OpenLayers Map object and save it to the ``m_map`` module variable when the module initializes. Having a handle on this object gives us full control over the map (see: `OpenLayers JavaScript API <https://openlayers.org/en/latest/apidoc/>`_). **Replace** the *INITIALIZATION / CONSTRUCTOR* section of :file:`public/js/gee_datasets.js` with the following:

.. code-block:: javascript

    /************************************************************************
    *                  INITIALIZATION / CONSTRUCTOR
    *************************************************************************/
    $(function() {
        // Initialize Global Variables
        bind_controls();

        // EE Products
        EE_PRODUCTS = $('#ee-products').data('ee-products');

        // Initialize values
        m_platform = $('#platform').val();
        m_sensor = $('#sensor').val();
        m_product = $('#product').val();
        INITIAL_START_DATE = m_start_date = $('#start_date').val();
        INITIAL_END_DATE = m_end_date = $('#end_date').val();
        m_reducer = $('#reducer').val();

        m_map = TETHYS_MAP_VIEW.getMap();
    });

5. Implement Adding Layers to the Map
=====================================

In this step you'll implement the new methods with logic to:

1. retrieve the XYZ map service URL by calling the new ``get-image-collection`` endpoint using AJAX and then
2. create a new OpenLayers ``Layer`` with an XYZ ``Source`` and add it to the map.

Here is a brief explanation of each method that will be implemented in this step:

* **update_map**: calls the ``get-image-collection`` endpoint using `jQuery.ajax() <https://api.jquery.com/jquery.ajax/>`_ passing it the current values of the controls.
* **create_data_layer**: creates a new ``ol.layer.Tile`` layer with an ``ol.source.XYZ`` source using the URL provided. The new layer is assigned to ``m_gee_layer`` so it can be reused in subsequent calls and then it is added to the map below the drawing layer (index 1) so that drawn features will show up on top.
* **update_data_layer**: creates the ``m_gee_layer`` if it doesn't exist or updates it if it does exist.

1. **Replace** the ``update_map`` method stub in :file:`public/js/gee_datasets.js` with the following implementation:

.. code-block:: javascript

    update_map = function() {
        let data = collect_data();

        let xhr = $.ajax({
            type: 'POST',
            url: 'get-image-collection/',
            dataType: 'json',
            data: data
        });

        xhr.done(function(response) {
            if (response.success) {
                console.log(response.url);
                update_data_layer(response.url);
            } else {
                alert('Oops, there was a problem loading the map you requested. Please try again.');
            }
        });
    };

2. **Update** the **Load** button ``click`` event, defined at the bottom of ``bind_controls`` method in :file:`public/js/gee_datasets.js`, to call ``update_map``:

.. code-block:: javascript

    $('#load_map').on('click', function() {
        update_map();
    });

.. warning::

    If you test the **Load** button at this point, the AJAX call to the ``get-image-collection`` endpoint will fail because it is missing the CSRF token. This token is used to verify that the call came from our client-side code and not from a site posing to be our site. As a security precaution, the server will reject any POST requests that do not include this token. You'll add the CSRF token in the next step. For more information about CSRF see: `Cross Site Request Forgery protection <https://docs.djangoproject.com/en/2.2/ref/csrf/>`_.

3. Add the following code to the :file:`public/js/main.js` file to automatically attach the CSRF Token to every AJAX request that needs it:

.. code-block:: javascript

    // Get a cookie
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie != '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // find if method is csrf safe
    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }

    // add csrf token to appropriate ajax requests
    $(function() {
        $.ajaxSetup({
            beforeSend: function(xhr, settings) {
                if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader("X-CSRFToken", getCookie("csrftoken"));
                }
            }
        });
    }); //document ready;

4. **Replace** the ``create_data_layer`` method stub in :file:`public/js/gee_datasets.js` with the following implementation:

.. code-block:: javascript

    create_data_layer = function(url) {
        let source = new ol.source.XYZ({
            url: url,
            attributions: '<a href="https://earthengine.google.com" target="_">Google Earth Engine</a>'
        });

        m_gee_layer = new ol.layer.Tile({
            source: source,
            opacity: 0.7
        });

        // Insert below the draw layer (so drawn polygons and points render on top of data layer).
        m_map.getLayers().insertAt(1, m_gee_layer);
    };

5. **Replace** the ``update_data_layer`` method stub in :file:`public/js/gee_datasets.js` with the following implementation:

.. code-block:: javascript

    update_data_layer = function(url) {
        if (!m_gee_layer) {
            create_data_layer(url);
        } else {
            m_gee_layer.getSource().setUrl(url);
        }
    };

6. Verify that the layers are being loaded on the map at this point. Browse to `<http://localhost:8000/apps/earth-engine>`_ in a web browser and login if necessary. Use the dataset controls to select a dataset product and press the **Load** button. Changing to a new dataset and pressing **Load** should replace the current layer with the new one.


6. Implement Clearing Layers on the Map
=======================================

Users can now visualize GEE layers on the map, but there is no way to clear the data from the map. In this step, you'll add a button that will remove layers and clear the map.

1. Add a **Clear** button to the ``home`` controller in :file:`controllers.py`:

.. code-block:: python

    clear_button = Button(
        name='clear_map',
        display_text='Clear',
        style='outline-secondary',
        attributes={'id': 'clear_map'},
        classes='mt-2',
    )

    context = {
        'platform_select': platform_select,
        'sensor_select': sensor_select,
        'product_select': product_select,
        'start_date': start_date,
        'end_date': end_date,
        'reducer_select': reducer_select,
        'load_button': load_button,
        'clear_button': clear_button,
        'ee_products': EE_PRODUCTS,
        'map_view': map_view
    }



2. Add the **Clear** button to the ``app_navigation_items`` block of the :file:`templates/earth_engine/home.html` template:

.. code-block:: html+django

    {% block app_navigation_items %}
      <li class="title">Select Dataset</li>
      {% gizmo platform_select %}
      {% gizmo sensor_select %}
      {% gizmo product_select %}
      {% gizmo start_date %}
      {% gizmo end_date %}
      {% gizmo reducer_select %}
      <p class="help">Change variables to select a data product, then press "Load" to add that product to the map.</p>
      {% gizmo load_button %}
      {% gizmo clear_button %}
    {% endblock %}

3. The ``clear_map`` method removes the layer from the map and removes all references to it. **Replace** the ``clear_map`` method stub in :file:`public/js/gee_datasets.js` with the following implementation:

.. code-block:: javascript

    clear_map = function() {
        if (m_gee_layer) {
            m_map.removeLayer(m_gee_layer);
            m_gee_layer = null;
        }
    };

4. Bind the ``clear_map`` method to the ``click`` event of the **Clear** button. Add the following to the bottom of the ``bind_controls`` method in :file:`public/js/gee_datasets.js`:

.. code-block:: javascript

    $('#clear_map').on('click', function() {
        clear_map();
    });

5. Verify that the **Clear** button works. Browse to `<http://localhost:8000/apps/earth-engine>`_ in a web browser and login if necessary. Load a dataset as before and then press the **Clear** button. The currently displayed layer should be removed from the map. Repeat this process a few times, loading several datasets before clearing at least one of the times to ensure it is working properly.

7. Implement Map Loading Indicator
==================================

You may have noticed while testing the app, that it can take some time for a layer to load. In this step you will add a loading image to indicate to the user that the map is loading, so they don't keep pressing the **Load** button impatiently.

1. Download this :download:`animated map loading image <./resources/map-loader.gif>` or find one that you like and save it to the :file:`public/images` directory.

2. Create a new stylesheet called :file:`public/css/loader.css` with styles for the loader image:

.. code-block:: css

    #loader {
        display: none;
        position: absolute;
        top: calc(50vh - 185px);
        left: calc(50vw - 186px);
    }

    #loader img {
        border-radius: 10%;
        box-shadow: 0 0 10px rgba(0, 0, 0, 0.2);
    }

    #loader.show {
        display: block;
    }

3. Include the new :file:`public/css/loader.css` and add the image to the ``after_app_content`` block of the :file:`templates/earth_engine/home.html` template:

.. code-block:: html+django

    {% block content_dependent_styles %}
        {{ block.super }}
        <link rel="stylesheet" href="{% static tethys_app|public:'css/map.css' %}" />
        <link rel="stylesheet" href="{% static tethys_app|public:'css/loader.css' %}" />
    {% endblock %}

.. code-block:: html+django

    {% block after_app_content %}
      <div id="ee-products" data-ee-products="{{ ee_products|jsonify }}"></div>
      <div id="loader">
        <img src="{% static tethys_app|public:'images/map-loader.gif' %}">
      </div>
    {% endblock %}



4. Show the loader image when the map starts loading tiles by binding to tile load events on the layer ``Source`` object when the layer is created. **Replace** the ``create_data_layer`` method in :file:`public/js/gee_datasets.js` with this new version:

.. code-block:: javascript

    create_data_layer = function(url) {
        let source = new ol.source.XYZ({
            url: url,
            attributions: '<a href="https://earthengine.google.com" target="_">Google Earth Engine</a>'
        });

        source.on('tileloadstart', function() {
            $('#loader').addClass('show');
        });

        source.on('tileloadend', function() {
            $('#loader').removeClass('show');
        });

        source.on('tileloaderror', function() {
            $('#loader').removeClass('show');
        });

        m_gee_layer = new ol.layer.Tile({
            source: source,
            opacity: 0.7
        });

        // Insert below the draw layer (so drawn polygons and points render on top of the data layer).
        m_map.getLayers().insertAt(1, m_gee_layer);
    };

8. Test and Verify
==================

Browse to `<http://localhost:8000/apps/earth-engine>`_ in a web browser and login if necessary. Verify the following:

1. Use the dataset controls to select a dataset and press the **Load** button to add it to the map.
2. Subsequent dataset loads should replace the previous dataset.
3. Use the **Clear** button to clear the map.
4. When a layer is loading tiles, a loading image should display to indicate to the user that the app is working.

9. Solution
===========

This concludes this portion of the GEE Tutorial. You can view the solution on GitHub at `<https://github.com/tethysplatform/tethysapp-earth_engine/tree/vis-gee-layers-solution-3.0>`_ or clone it as follows:

.. parsed-literal::

    git clone https://github.com/tethysplatform/tethysapp-earth_engine
    cd tethysapp-earth_engine
    git checkout -b vis-gee-layers-solution vis-gee-layers-solution-|version|
