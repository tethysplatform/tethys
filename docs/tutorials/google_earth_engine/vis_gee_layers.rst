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

4. Implement the `get_image_collection_asset` function as follows:

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

5. Implement the `image_to_map_id` function as follows:

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

1. Add a new controller called `get_image_collection` to :file:`controllers.py`:

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

2. Add a new `UrlMap` to the `url_maps` method of the :term:`app class` in :file:`app.py`:

.. code-block:: python

    UrlMap(
        name='get_image_collection',
        url='earth-engine/get-image-collection',
        controller='earth_engine.controllers.get_image_collection'
    ),

3. Stub out the Map JavaScript Methods
======================================

1. Add the following module level variables in :file:`public/js/gee_datasets.js`:

.. code-block:: javascript

    // Map Variables
 	var m_map,
 	    m_gee_layer;

2. Add the following module method declarations in :file:`public/js/gee_datasets.js`:

.. code-block:: javascript

    // Map Methods
 	var update_map, update_data_layer, create_data_layer, clear_map;

3. Add the following module method stubs in :file:`public/js/gee_datasets.js`:

.. code-block:: javascript

    // Map Methods
    update_map = function() {};

    update_data_layer = function(url) {};

    create_data_layer = function(url) {};

    clear_map = function() {};

4. Implement Adding Layers to the Map
=====================================

1. Implement the `update_map` method in :file:`public/js/gee_datasets.js`:

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

2. Call `update_map` when the `Load` button is clicked (in `bind_controls` method):

.. code-block:: javascript

    $('#load_map').on('click', function() {
        update_map();
    });

3. Implement the `update_data_layer` method in :file:`public/js/gee_datasets.js`

.. code-block:: javascript

    update_data_layer = function(url) {
        if (!m_gee_layer) {
            create_data_layer(url);
        } else {
            m_gee_layer.getSource().setUrl(url);
        }
    };

4. Implement the `create_data_layer` method in :file:`public/js/gee_datasets.js`

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

1. Add `Clear` button to `home` controller in :file:`controllers.py`:

.. code-block:: python

2. Add `Clear` button to :file:`home.html` template:

.. code-block:: html+django

3. Implement `clear_map` method in :file:`public/js/gee_datasets.js`:

.. code-block:: javascript



6. Implement Map Loading Indicator
==================================

1. Add
