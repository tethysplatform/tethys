**************************************
Visualize Google Earth Engine Datasets
**************************************

**Last Updated:** November 2019

1. Write Needed GEE Logic
=========================

1. Create a new Python module in the :file:`gee` package called :file:`params.py` with the following contents:

.. code-block:: python

    service_account = ''  # your google service account
    private_key = ''  # path to the json private key for the service account

2. Create a new Python module in the :file:`gee` package called :file:`cloud_mask.py` with the following contents:

.. code-block:: python

    import ee


    def mask_l8_sr(image):
        """
        Derived From: https://developers.google.com/earth-engine/datasets/catalog/LANDSAT_LC08_C01_T1_SR
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
        Derived From: https://developers.google.com/earth-engine/datasets/catalog/LANDSAT_LE07_C01_T1_SR
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
        Derived from: https://developers.google.com/earth-engine/datasets/catalog/COPERNICUS_S2
        """
        qa = image.select('QA60')

        # Bits 10 and 11 are clouds and cirrus, respectively.
        cloudBitMask = 1 << 10
        cirrusBitMask = 1 << 11

        # Both flags should be set to zero, indicating clear conditions.
        mask = qa.bitwiseAnd(cloudBitMask).eq(0).And(qa.bitwiseAnd(cirrusBitMask).eq(0))

        return image.updateMask(mask).divide(10000)

3. Create a new Python module in the :file:`gee` package called :file:`methods.py` with the following contents:

.. todo::

    Discuss authentication with Google Earth Engine in production: https://developers.google.com/earth-engine/service_account

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
            from oauth2client.service_account import ServiceAccountCredentials
            credentials = ServiceAccountCredentials.from_p12_keyfile(
                service_account_email='',
                filename='',
                private_key_password='notasecret',
                scopes=ee.oauth.SCOPE + ' https://www.googleapis.com/auth/drive '
            )
            ee.Initialize(credentials)


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

4. Implement the ``get_image_collection_asset`` function as follows:

.. todo::

    Discuss Map Services and the XYZ services that we will be building a URL for. Find GEE docs on this.

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

        tile_url_template = "https://earthengine.googleapis.com/map/{mapid}/{{z}}/{{x}}/{{y}}?token={token}"

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

            map_id_params = image_to_map_id(ee_collection, vis_params)

            return tile_url_template.format(**map_id_params)

        except EEException:
            log.exception('An error occurred while attempting to retrieve the image collection asset.')

5. Implement the ``image_to_map_id`` function as follows:

.. code-block:: python

    def image_to_map_id(image_name, vis_params={}):
        """
        Get map_id parameters
        """
        try:
            ee_image = ee.Image(image_name)
            map_id = ee_image.getMapId(vis_params)
            map_id_params = {
                'mapid': map_id['mapid'],
                'token': map_id['token']
            }
            return map_id_params

        except EEException:
            log.exception('An error occurred while attempting to retrieve the map id.')

2. Create Endpoint for Getting Map Images
=========================================

1. Add a new controller called ``get_image_collection`` to :file:`controllers.py`:

.. todo::

    Introduce logging

.. code-block:: python

    import logging
    from django.http import JsonResponse, HttpResponseNotAllowed
    from .gee.methods import get_image_collection_asset

    log = logging.getLogger(f'tethys.apps.{__name__}')

    ...

    @login_required()
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

2. Add a new ``UrlMap`` to the ``url_maps`` method of the :term:`app class` in :file:`app.py`:

.. code-block:: python

    UrlMap(
        name='get_image_collection',
        url='earth-engine/get-image-collection',
        controller='earth_engine.controllers.get_image_collection'
    ),

3. Stub Out the Map JavaScript Methods
======================================

1. Add the following module level variables in :file:`public/js/gee_datasets.js`:

.. code-block:: javascript

    // Map Variables
 	var m_map,
 	    m_gee_layer;

2. Add the following module function declarations in :file:`public/js/gee_datasets.js` below the dataset select function declarations:

.. code-block:: javascript

    // Map Methods
 	var update_map, update_data_layer, create_data_layer, clear_map;

3. Add the following module function stubs in :file:`public/js/gee_datasets.js`, just below the ``collect_data`` implementation:

.. code-block:: javascript

    // Map Methods
    update_map = function() {};

    update_data_layer = function(url) {};

    create_data_layer = function(url) {};

    clear_map = function() {};

4. Retrieve the ``TethyMapView`` OpenLayers ``Map`` object when the module initializes:

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

4. Implement Adding Layers to the Map
=====================================

1. Implement the ``update_map`` method in :file:`public/js/gee_datasets.js`:

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

2. Call ``update_map`` when the ``Load`` button is clicked (in ``bind_controls`` method):

.. code-block:: javascript

    $('#load_map').on('click', function() {
        update_map();
    });

.. todo::

    Testing at this point will demonstrate the need for the csrf_token, b/c it sends an AJAX POST request. Discuss the cookie that is used for this purpose.

3. Add the following code to the :file:`public/js/main.js` file to automatically attach the CSRF Token to each AJAX request:

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

4. Implement the ``update_data_layer`` method in :file:`public/js/gee_datasets.js`

.. code-block:: javascript

    update_data_layer = function(url) {
        if (!m_gee_layer) {
            create_data_layer(url);
        } else {
            m_gee_layer.getSource().setUrl(url);
        }
    };

5. Implement the ``create_data_layer`` method in :file:`public/js/gee_datasets.js`

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


5. Implement Clearing Layers on the Map
=======================================

1. Add ``Clear`` button to ``home`` controller in :file:`controllers.py`:

.. code-block:: python

    clear_button = Button(
        name='clear_map',
        display_text='Clear',
        style='default',
        attributes={'id': 'clear_map'}
    )

    ...

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



2. Add ``Clear`` button to the ``app_navigation_items`` block of the :file:`templates/earth_engine/home.html` template:

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

3. Implement ``clear_map`` method in :file:`public/js/gee_datasets.js`:

.. code-block:: javascript

    clear_map = function() {
        if (m_gee_layer) {
            m_map.removeLayer(m_gee_layer);
            m_gee_layer = null;
        }
    };

4. Bind the ``clear_map`` method to the ``on-click`` event of the ``clear_map`` button (in the ``bind_controls`` method):

.. code-block:: javascript

    $('#clear_map').on('click', function() {
        clear_map();
    });

6. Implement Map Loading Indicator
==================================

1. Download this :download:`Google Earth Engine App Icon <./resources/map-loader.gif>` or find one that you like and save it to the :file:`public/images` directory.

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

3. Add the image to the `after_app_content` block of the :file:`templates/earth_engine/home.html` template and include the new :file:`public/css/loader.css`:

.. code-block:: html+django

    {% block content_dependent_styles %}
        {{ block.super }}
        <link rel="stylesheet" href="{% static 'earth_engine/css/map.css' %}" />
        <link rel="stylesheet" href="{% static 'earth_engine/css/loader.css' %}" />
    {% endblock %}

.. code-block:: html+django

    {% block after_app_content %}
      <div id="ee-products" data-ee-products="{{ ee_products|jsonify }}"></div>
      <div id="loader">
        <img src="{% static 'earth_engine/images/map-loader.gif' %}">
      </div>
    {% endblock %}



4. Show the loader image when the map starts loading tiles by binding to tile load events on the layer ``Source``. Update the ``create_data_layer`` method in :file:`public/js/gee_datasets.js`:

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

        // Insert below the draw layer (so drawn polygons and points render on top of data layer).
        m_map.getLayers().insertAt(1, m_gee_layer);
    };
