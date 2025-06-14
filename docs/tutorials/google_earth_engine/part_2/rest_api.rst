**************
Add a REST API
**************

**Last Updated:** July 2024

In this tutorial you will add a REST API endpoint to the Earth Engine app. The REST API will provide a programmatic access point to the underlying ``get_time_series_from_image_collection`` method. This is the same method that is used retrieve the time series for the plot at an area of interest capability of the Viewer page. Topics covered in this tutorial include:

* :ref:`tethys_rest_api` in Tethys Apps
* `Django REST Framework <https://www.django-rest-framework.org/>`_ in Tethys
* Token Authentication
* Controllers in Multiple Files
* Developing REST APIs with `Postman <https://www.postman.com/>`_

.. figure:: ../../../images/tutorial/gee/rest_api.png
    :width: 800px
    :align: center

0. Start From Previous Solution (Optional)
==========================================

If you wish to use the previous solution as a starting point:

.. parsed-literal::

    git clone https://github.com/tethysplatform/tethysapp-earth_engine
    cd tethysapp-earth_engine
    git checkout -b clip-by-asset-solution clip-by-asset-solution-|version|

1. Install dependencies
=======================

The REST API capability requires ``djangorestframework`` to be installed. Install it using conda or pip as follows:

.. code-block:: bash

    # conda: conda-forge channel strongly recommended
    conda install -c conda-forge djangorestframework

    # pip
    pip install djangorestframework

2. Add dependencies to install.yml
==================================

Add ``djangorestframework`` to the ``install.yml`` file to ensure it is installed when your app is installed as follows:

.. code-block:: yaml

    # This file should be committed to your app code.
    version: 1.0
    # This should be greater or equal to your tethys-platform in your environment
    tethys_version: ">=4.0.0"
    # This should match the app - package name in your setup.py
    name: earth_engine

    requirements:
        # Putting in a skip true param will skip the entire section. Ignoring the option will assume it be set to False
        skip: false
        conda:
            channels:
            - conda-forge
            packages:
            - earthengine-api
            - oauth2client
            - geojson
            - pandas
            - pyshp
            - simplejson
            - djangorestframework
        pip:

        npm:

    post:

3. Reorganize Controller Functions into Separate Files
======================================================

The :file:`controllers.py` file is beginning to get quite long. To make the controller code more manageable, in this step you will refactor the controllers into several files.

1. Create a new folder called :file:`controllers` in the :file:`earth_engine` directory with the following new empty Python modules in it:

* :file:`controllers/`
    * :file:`__init__.py`
    * :file:`home.py`
    * :file:`viewer.py`
    * :file:`rest.py`

.. note::

    A folder with a file named :file:`__init__.py` is called a Python package.

.. warning::

    If you are using PyCharm, make sure it doesn't add an :file:`__init__.py` file in the :file:`tethysapp` directory. This will cause this app or other apps to stop working when installed in Tethys Platform.

2. Copy the ``home`` and ``about`` controller functions, with any imports they need into the new :file:`controllers/home.py` module:

.. code-block:: python

    import logging
    from tethys_sdk.routing import controller

    from ..app import App 

    log = logging.getLogger(f'tethys.apps.{__name__}')


    @controller
    def home(request):
        """
        Controller for the app home page.
        """
        context = {}
        return App.render(request, 'home.html', context)


    @controller
    def about(request):
        """
        Controller for the app about page.
        """
        context = {}
        return App.render(request, 'about.html', context)

3. Copy the ``viewer``, ``get_image_collection``, and ``get_time_series_plot`` controller functions with any imports they need into the new :file:`controllers/viewer.py` module:

.. code-block:: python

    import datetime as dt
    import geojson
    import logging
    from simplejson.errors import JSONDecodeError

    from django.http import JsonResponse, HttpResponseNotAllowed, HttpResponseRedirect
    from tethys_sdk.routing import controller
    from tethys_sdk.gizmos import SelectInput, DatePicker, Button, MapView, MVView, PlotlyView, MVDraw

    from ..app import App

    from ..helpers import generate_figure, handle_shapefile_upload
    from ..gee.methods import get_image_collection_asset, get_time_series_from_image_collection, \
        get_boundary_fc_props_for_user
    from ..gee.products import EE_PRODUCTS

    log = logging.getLogger(f'tethys.apps.{__name__}')

.. code-block:: python

    @controller(user_media=True, url='viewer')
    def viewer(request, user_media):
        """
        Controller for the app viewer page.
        """

        ...  # Code not shown for brevity

        return App.render(request, 'viewer.html', context)


    @controller(url='viewer/get-image-collection')
    def get_image_collection(request):
        """
        Controller to handle image collection requests.
        """

        ...  # Code not shown for brevity

        return JsonResponse(response_data)


    @controller(url='viewer/get-time-series-plot')
    def get_time_series_plot(request):

        ...  # Code not shown for brevity

        return App.render(request, 'plot.html', context)

5. Delete the old :file:`controllers.py` file.

6. Navigate to `<http://localhost:8000/apps/earth-engine/>`_ and verify that the app functions as it did before the change.

4. Create New Controller for REST API Endpoint
==============================================

REST endpoints are similar to normal controllers. The primary difference is that they typically return data using JSON or XML format instead of HTML. In this step you will create a new controller function for the REST endpoint.

1. Create a new controller function named ``get_time_series`` in :file:`controllers/rest.py` with the following contents:

.. code-block:: python

    import logging
    from django.http import JsonResponse
    from tethys_sdk.routing import controller
    from rest_framework.authentication import TokenAuthentication
    from rest_framework.decorators import api_view, authentication_classes

    log = logging.getLogger(f'tethys.apps.{__name__}')


    @controller(url='api/get-time-series', login_required=False)
    @api_view(['GET', 'POST'])
    @authentication_classes((TokenAuthentication,))
    def get_time_series(request):
        """
        Controller for the get-time-series REST endpoint.
        """
        response_data = {
            "detail": "Hello, World!"
        }
        return JsonResponse(response_data)

.. tip::

    Tethys includes the `Django REST Framework <https://www.django-rest-framework.org/>`_ to aid with the token authentication capability (i.e. ``api_view()`` and ``authentication_classes()`` decorators). It is quite a capable extension for Django websites and is worth investigating if you plan to make a large, stand alone REST API.

3. Navigate to `<http://localhost:8000/apps/earth-engine/api/get-time-series/>`_. You should see an API page that is auto generated by the `Django REST Framework <https://www.django-rest-framework.org/>`_ titled **Get Time Series**. The page should display an *HTTP 401 Unauthorized* error and display a result object with detail "Authentication credentials were not provided."

5. Test with Postman Application
================================

Most web browsers are surprisingly limited when it comes to testing REST APIs. The reason the test in the previous step resulted in a *401 Unauthorized* is because we sent a request without an authentication token. To more easily test this, you'll want to get a REST client that will allow you to set request headers and parameters. In this tutorial you will use the Postman client to test the REST API as you develop it.

1. If you have not done so already, `download and install the Postman app <https://www.postman.com/>`_ and then launch it.

2. In Postman click on the **New** button and select **Collection**.

3. Name the collection "Earth Engine App API" and press the **Create** button.

4. Right-click on the new *Earth Engine App API* collection or click on it's "**...**" button and select **Add Request**.

5. Name the new request "get-time-series" and press the **Save to Earth Engine App API** button.

6. From the menu on the left, expand the *Earth Engine App API* collection and click on the *get-time-series* request to open it in a new tab.

7. Select **GET** as the method and enter "http://localhost:8000/apps/earth-engine/api/get-time-series/" in the URL field.

8. Press the **Save** button to save changes.

9. Press the **Send** button. You should see the same response object as before with the "Authentication credentials were not provided." message.

6. Add Token Authorization Headers to Postman Request
=====================================================

In this step you will retrieve the API token for your user account and set authentication headers on the request.

1. Navigate to `<http://localhost:8000/apps/>`_ and sign in if necessary.

2. Click on the button with your username on it in the top-right-hand corner of the page to access your user profile.

3. Copy the value of the API Key.

4. In Postman, click on the Authorization tab, just under the URL field.

5. Select "API Key" as the **TYPE** and enter "Authorization" for the **Key** and "Token <your token>" for the value (replace ``<your token>`` with the token you copied).

6. Press the **Send** button again. This time the request should be sent with the proper authorization token. You should see a response object with the "Hello, World!" message.

7. Press the **Save** button to save your changes to the Postman request.

7. Define Parameters for REST API
=================================

In this step you'll define the parameters that the REST endpoint will accept. If you think of the REST endpoint as a function, then the parameters are like the arguments to the function. The controller will be configured to work with both the ``GET`` and ``POST`` methods for illustration purposes.

1. Update the ``get_time_series`` controller in :file:`controllers/rest.py` as follows:

.. code-block:: python

    from django.http import HttpResponseBadRequest

.. code-block:: python

    @controller(url='api/get-time-series', login_required=False)
    @api_view(['GET', 'POST'])
    @authentication_classes((TokenAuthentication,))
    def get_time_series(request):
        """
        Controller for the get-time-series REST endpoint.
        """
        # Get request parameters.
        if request.method == 'GET':
            data = request.GET.copy()
        elif request.method == 'POST':
            data = request.POST.copy()
        else:
            return HttpResponseBadRequest('Only GET and POST methods are supported.')

        platform = data.get('platform', None)
        sensor = data.get('sensor', None)
        product = data.get('product', None)
        start_date_str = data.get('start_date', None)
        end_date_str = data.get('end_date', None)
        reducer = data.get('reducer', 'median')
        index = data.get('index', None)
        scale_str = data.get('scale', 250)
        orient = data.get('orient', 'list')
        geometry_str = data.get('geometry', None)

        # compose response object.
        response_data = {
            'parameters': {
                'platform': platform,
                'sensor': sensor,
                'product': product,
                'index': index,
                'start_date': start_date_str,
                'end_date': end_date_str,
                'reducer': reducer,
                'geometry': geometry_str
            }
        }

        return JsonResponse(response_data)

2. In Postman, select the **Params** tab.

3. Click on the **Bulk Edit** link on the right and enter the following:

.. code-block::

    platform:modis
    sensor:terra
    product:temperature
    start_date:2020-02-15
    end_date:2020-04-14
    reducer:mean
    //index:NDVI
    geometry:{"type":"GeometryCollection","geometries":[{"type":"Point","coordinates":[36.112060546875,-0.03295898255728957],"properties":{"id":"drawing_layer.79c08238-4084-4825-9e76-f018527d45b7"},"crs":{"type":"link","properties":{"href":"http://spatialreference.org/ref/epsg/4326/proj4/","type":"proj4"}}},{"type":"Polygon","coordinates":[[[36.749267578125,0.1867672473697155],[36.6943359375,-0.043945308191354115],[36.99096679687499,-0.043945308191354115],[36.9140625,0.1757809742470755],[36.749267578125,0.1867672473697155]]],"properties":{"id":"drawing_layer.ffa36dfd-5767-4946-890b-f4c0d9c0ff9f"},"crs":{"type":"link","properties":{"href":"http://spatialreference.org/ref/epsg/4326/proj4/","type":"proj4"}}}]}
    orient:series
    scale:250

4. Click on the **Key-Value Edit** link on the right. Notice how the *Query Params* key-value form is populated with values. Also, notice that the same parameters are added to the URL as query parameters (i.e. ``?key1=value1&key2=value2``).

    .. note::

        The ``index`` parameter should be unchecked / disabled.

5. Press the **Send** button and verify that the parameters are returned in the response object.

6. Press the **Save** button to save your changes to the Postman request.

8. Validate Platform, Sensor, Product, and Index
================================================

In this step you'll add the validation logic for the ``platform``, ``sensor``, ``product``, and ``index`` parameters. The REST endpoint is like a function shared publicly on the internet--anyone can call it with whatever parameters they want. This includes bots that may try to exploit your website through its REST endpoints. Be sure to only allow valid values through and provide helpful feedback for users of the REST API.

1. Modify the ``get_time_series`` controller in :file:`controllers/rest.py` to add validation for the ``platform``, ``sensor``, ``product``, and ``index`` parameters as follows:

.. code-block:: python

    from ..gee.products import EE_PRODUCTS

.. code-block:: python
    :emphasize-lines: 27-57

    @controller(url='api/get-time-series')
    @api_view(['GET', 'POST'])
    @authentication_classes((TokenAuthentication,))
    def get_time_series(request):
        """
        Controller for the get-time-series REST endpoint.
        """
        # Get request parameters.
        if request.method == 'GET':
            data = request.GET.copy()
        elif request.method == 'POST':
            data = request.POST.copy()
        else:
            return HttpResponseBadRequest('Only GET and POST methods are supported.')

        platform = data.get('platform', None)
        sensor = data.get('sensor', None)
        product = data.get('product', None)
        start_date_str = data.get('start_date', None)
        end_date_str = data.get('end_date', None)
        reducer = data.get('reducer', 'median')
        index = data.get('index', None)
        scale_str = data.get('scale', 250)
        orient = data.get('orient', 'dict')
        geometry_str = data.get('geometry', None)

        # validate given parameters
        # platform
        if not platform or platform not in EE_PRODUCTS:
            valid_platform_str = '", "'.join(EE_PRODUCTS.keys())
            return HttpResponseBadRequest(f'The "platform" parameter is required. Valid platforms '
                                          f'include: "{valid_platform_str}".')

        # sensors
        if not sensor or sensor not in EE_PRODUCTS[platform]:
            valid_sensor_str = '", "'.join(EE_PRODUCTS[platform].keys())
            return HttpResponseBadRequest(f'The "sensor" parameter is required. Valid sensors for the "{platform}" '
                                          f'platform include: "{valid_sensor_str}".')

        # product
        if not product or product not in EE_PRODUCTS[platform][sensor]:
            valid_product_str = '", "'.join(EE_PRODUCTS[platform][sensor].keys())
            return HttpResponseBadRequest(f'The "product" parameter is required. Valid products for the "{platform} '
                                          f'{sensor}" sensor include: "{valid_product_str}".')

        selected_product = EE_PRODUCTS[platform][sensor][product]

        # index
        # if index not provided, get default index from product properties
        if not index:
            index = selected_product['index']

        # if index is still None (not defined for the product) it is not supported currently
        if index is None:
            return HttpResponseBadRequest(
                f'Retrieving time series for "{platform} {sensor} {product}" is not supported at this time.'
            )

        # compose response object.
        response_data = {
            'parameters': {
                'platform': platform,
                'sensor': sensor,
                'product': product,
                'index': index,
                'start_date': start_date_str,
                'end_date': end_date_str,
                'reducer': reducer,
                'geometry': geometry_str
            }
        }

        return JsonResponse(response_data)

2. In Postman, select the **Params** tab if not already active.

3. Uncheck all of the parameters so that they are not included in the request.

4. Press the **Send** button and verify that the status code *400 Bad Request* is returned (see top-right side of the response section) and the validation message for the ``platform`` parameter is returned.

5. Add the ``platform`` parameter to the request by checking the box next to it.

6. Press the **Send** button and verify that the status code *400 Bad Request* is returned (see top-right side of the response section) and the validation message for the ``sensor`` parameter is returned.

7. Change the value of the ``platform`` parameter to "landsat" or "sentinel" and verify that the validation message for the ``sensor`` parameter lists the appropriate sensors.

8. Change the ``platform`` parameter back to "modis".

9. Repeat this process, adding first the ``sensor`` parameter, then the ``product`` parameter to confirm that the validation logic is working as expected.

9. Validate Dates
=================

In this step you'll add the validation logic for the ``start_date`` and ``end_date`` parameters. There is logic that already exists in the ``viewer`` controller that you can use to validate the date parameters in our REST API function. However, you should avoid copying code to prevent duplicating bugs and make the app easier to maintain. Instead, you will generalize the bit of code from the ``viewer`` controller into a helper function and then use that function in both the ``viewer`` controller and the ``get_time_series`` controller.

1. Create a new helper function called ``compute_dates_for_product`` in :file:`helpers.py` with contents based on the validation logic for dates in the ``viewer`` controller:

.. code-block:: python

    import datetime as dt

.. code-block:: python

    def compute_dates_for_product(product_dict):
        """
        Compute default dates and date range for given product.

        Args:
            product_dict (dict): The product dictionary from EE_PRODUCTS

        Returns:
            dict<default_start_date,default_end_date,beg_valid_date_range,end_valid_date_range>: dict with date strings formatted: %Y-%m-%d.
        """
        # Hardcode initial end date to today (since all of our datasets extend to present)
        today = dt.datetime.today()
        default_end_date = today.strftime('%Y-%m-%d')

        # Initial start date will a set number of days before the end date
        # NOTE: This assumes the start date of the dataset is at least 30+ days prior to today
        default_end_date_dt = dt.datetime.strptime(default_end_date, '%Y-%m-%d')
        default_start_date_dt = default_end_date_dt - dt.timedelta(days=30)
        default_start_date = default_start_date_dt.strftime('%Y-%m-%d')

        # Get valid date range for product
        beg_valid_date_range = product_dict.get('start_date', None)
        end_valid_date_range = product_dict.get('end_date', None) or default_end_date

        product_dates = {
            'default_start_date': default_start_date,
            'default_end_date': default_end_date,
            'beg_valid_date_range': beg_valid_date_range,
            'end_valid_date_range': end_valid_date_range
        }

        return product_dates

.. tip::

    Compare this function with similar logic in the ``viewer`` controller. Many of the variables have been renamed to make it more general, but the functionality is mostly the same.

2. Import the new ``compute_dates_for_product`` helper function and then refactor the ``viewer`` controller in :file:`controllers/viewer.py`` to use the new ``compute_dates_for_product`` helper function. Replace all of the previous date logic in the ``viewer`` controller starting with the line with comment ``# Hardcode initial end date ...`` and ending with the ``end_date`` ``DatePicker``:

.. code-block:: python

    from ..helpers import compute_dates_for_product

.. code-block:: diff

    -# Hardcode initial end date to today (since all of our datasets extend to present)
    -today = dt.datetime.today()
    -initial_end_date = today.strftime('%Y-%m-%d')
    
    -# Initial start date will a set number of days before the end date
    -# NOTE: This assumes the start date of the dataset is at least 30+ days prior to today
    -initial_end_date_dt = dt.datetime.strptime(initial_end_date, '%Y-%m-%d')
    -initial_start_date_dt = initial_end_date_dt - dt.timedelta(days=30)
    -initial_start_date = initial_start_date_dt.strftime('%Y-%m-%d')
 
    -# Build date controls
    -first_product_start_date = first_product.get('start_date', None)
    -first_product_end_date = first_product.get('end_date', None) or initial_end_date
 
    +# Get initial default dates and date ranges for date picker controls
    +first_product_dates = compute_dates_for_product(first_product)
 
     start_date = DatePicker(
         name='start_date',
         display_text='Start Date',
         format='yyyy-mm-dd',
         start_view='decade',
         today_button=True,
         today_highlight=True,
    +    start_date=first_product_dates['beg_valid_date_range'],
    +    end_date=first_product_dates['end_valid_date_range'],
    +    initial=first_product_dates['default_start_date'],
         autoclose=True
     )
 
     end_date = DatePicker(
         name='end_date',
         display_text='End Date',
         format='yyyy-mm-dd',
         start_view='decade',
         today_button=True,
         today_highlight=True,
    +    start_date=first_product_dates['beg_valid_date_range'],
    +    end_date=first_product_dates['end_valid_date_range'],
    +    initial=first_product_dates['default_end_date'],
         autoclose=True
     )

3. Modify the ``get_time_series`` controller in :file:`controllers/rest.py` to also use the ``compute_dates_for_product`` helper function as part of it's validation for the ``start_date`` and ``end_date`` parameters. Replace the ``response_data`` object with the following:

.. code-block:: python

    import datetime as dt
    from ..helpers import compute_dates_for_product

.. code-block:: python

    # get valid dates for selected product
    product_dates = compute_dates_for_product(selected_product)

    # assign default start date if not provided
    if not start_date_str:
        start_date_str = product_dates['default_start_date']

    # assign default start date if not provided
    if not end_date_str:
        end_date_str = product_dates['default_end_date']

    # convert to datetime objects for validation
    try:
        start_date_dt = dt.datetime.strptime(start_date_str, '%Y-%m-%d')
        end_date_dt = dt.datetime.strptime(end_date_str, '%Y-%m-%d')
    except ValueError:
        return HttpResponseBadRequest(
            'Invalid date format. Please use "YYYY-MM-DD".'
        )

    beg_valid_date_range = dt.datetime.strptime(product_dates['beg_valid_date_range'], '%Y-%m-%d')
    end_valid_date_range = dt.datetime.strptime(product_dates['end_valid_date_range'], '%Y-%m-%d')

    # start_date in valid range
    if start_date_dt < beg_valid_date_range or start_date_dt > end_valid_date_range:
        return HttpResponseBadRequest(
            f'The date {start_date_str} is not a valid "start_date" for "{platform} {sensor} {product}". '
            f'It must occur between {product_dates["beg_valid_date_range"]} '
            f'and {product_dates["end_valid_date_range"]}.'
        )

    # end_date in valid range
    if end_date_dt < beg_valid_date_range or end_date_dt > end_valid_date_range:
        return HttpResponseBadRequest(
            f'The date {end_date_str} is not a valid "end_date" for "{platform} {sensor} {product}". '
            f'It must occur between {product_dates["beg_valid_date_range"]} '
            f'and {product_dates["end_valid_date_range"]}.'
        )

    # start_date before end_date
    if start_date_dt > end_date_dt:
        return HttpResponseBadRequest(
            f'The "start_date" must occur before the "end_date". Dates given: '
            f'start_date = {start_date_str}; end_date = {end_date_str}.'
        )

    # compose response object.
    response_data = {
        'parameters': {
            'platform': platform,
            'sensor': sensor,
            'product': product,
            'index': index,
            'start_date': start_date_str,
            'end_date': end_date_str,
            'reducer': reducer,
            'geometry': geometry_str
        }
    }

    return JsonResponse(response_data)


4. Use Postman to send a request with only the ``platform``, ``sensor``, and ``product`` parameters. Ensure that the values given for the enabled parameters are valid. Verify that ``end_date`` is returned as today's date and that the ``start_date`` is 30 days prior to today's date.

5. Add the ``start_date`` parameter and send another request. Verify that the same date sent is returned as the ``start_date``.

6. Add the ``end_date`` parameter and send another request. Verify that the same date sent is returned as the ``end_date``.

7. Also test different values for dates to test the following scenarios:

    * ``start_date`` == ``end_date``
    * ``start_date`` > ``end_date``
    * ``start_date`` outside of valid range of selected product (see :file:`gee/products.py`)
    * ``end_date`` outside of valid range of selected product (see :file:`gee/products.py`)
    * ``start_date`` and ``end_date`` outside of valid range of selected product (see :file:`gee/products.py`)
    * Incorrect date format given for either date parameter

10. Validate Reducer, Orient, and Scale
=======================================

In this step you'll add the validation logic for the ``reducer``, ``orient``, and ``scale`` parameters. The ``reducer`` and ``orient`` parameters each have a short list of valid options and the ``scale`` parameter needs to be a number.

1. Modify the ``get_time_series`` controller in :file:`controllers/rest.py` to add validation for the ``reducer``, ``orient``, and ``scale`` parameters. Replace the ``response_data`` object with the following:

.. code-block:: python

    # reducer
    valid_reducers = ('median', 'mosaic', 'mode', 'mean', 'min', 'max', 'sum', 'count', 'product')
    if reducer not in valid_reducers:
        valid_reducer_str = '", "'.join(valid_reducers)
        return HttpResponseBadRequest(
            f'The value "{reducer}" is not valid for parameter "reducer". '
            f'Must be one of: "{valid_reducer_str}". Defaults to "median" '
            f'if not given.'
        )

    # orient
    valid_orient_vals = ('dict', 'list', 'series', 'split', 'records', 'index')
    if orient not in valid_orient_vals:
        valid_orient_str = '", "'.join(valid_orient_vals)
        return HttpResponseBadRequest(
            f'The value "{orient}" is not valid for parameter "orient". '
            f'Must be one of: "{valid_orient_str}". Defaults to "dict" '
            f'if not given.'
        )

    # scale
    try:
        scale = float(scale_str)
    except ValueError:
        return HttpResponseBadRequest(
            f'The "scale" parameter must be a valid number, but "{scale_str}" was given.'
        )

    # compose response object.
    response_data = {
        'parameters': {
            'platform': platform,
            'sensor': sensor,
            'product': product,
            'index': index,
            'start_date': start_date_str,
            'end_date': end_date_str,
            'reducer': reducer,
            'orient': orient,
            'scale': scale,
            'geometry_str': geometry_str
        }
    }

    return JsonResponse(response_data)

2. Use Postman to send a request with only the ``platform``, ``sensor``, ``product``, ``start_date`` and ``end_date`` parameters. Ensure that the values given for the enabled parameters are valid. Verify that the default values for ``reducer``, ``orient``, and ``scale`` are returned.

3. Add the ``reducer`` parameter with an invalid value (e.g. ``foo``). Verify that the validation message is displayed and lists valid values for ``reducer``.

4. Change ``reducer`` to a valid value other than the default (e.g.: ``mean``). Verify this value is returned.

5. Add the ``orient`` parameter with an invalid value (e.g. ``foo``). Verify that the validation message is displayed and lists valid values for ``orient``.

6. Change ``orient`` to a valid value other than the default (e.g.: ``series``). Verify this value is returned.

7. Add the ``scale`` parameter with a non-numeric value (e.g.: ``foo``). Verify that the validation message is displayed for ``scale``.

8. Change ``scale`` to a valid value other than the default (e.g.: ``150``). Verify this value is returned.

11. Validate Geometry
=====================

In this step you'll add the logic to validate the ``geometry`` parameter, which should be valid GeoJSON. An optimistic strategy will be used in which an attempt will be made to convert the string into a GeoJSON object. If it fails, then the given string is not valid GeoJSON and an error will be returned.

1. Modify the ``get_time_series`` controller in :file:`controllers/rest.py` to add validation for the ``geometry`` parameter.  Replace the ``response_data`` object with the following:

.. code-block:: python

    import geojson
    from simplejson import JSONDecodeError

.. code-block:: python
    :emphasize-lines: 1

    # geometry
    bad_geometry_msg = 'The "geometry" parameter is required and must be a valid geojson string.'
    if not geometry_str:
        return HttpResponseBadRequest(bad_geometry_msg)

    try:
        geometry = geojson.loads(geometry_str)
    except JSONDecodeError:
        return HttpResponseBadRequest(bad_geometry_msg)

    # compose response object.
    response_data = {
        'parameters': {
            'platform': platform,
            'sensor': sensor,
            'product': product,
            'index': index,
            'start_date': start_date_str,
            'end_date': end_date_str,
            'reducer': reducer,
            'orient': orient,
            'scale': scale,
            'geometry': geometry
        }
    }

    return JsonResponse(response_data)


2. Use Postman to send a request with only the ``platform``, ``sensor``, ``product``, ``start_date``, ``end_date``, ``reducer``, ``orient``, and ``scale`` parameters. Ensure that the values given for the enabled parameters are valid. Verify that a message indicating that the ``geometry`` parameter is required is returned.

3. Add the ``geometry`` parameter with an invalid value (e.g. ``foo``). Verify that the validation message is displayed and indicates that the geometry parameter must be GeoJSON.

4. Change ``geometry`` to the following and verify this value is returned:

.. code-block:: json

    {"type":"GeometryCollection","geometries":[{"type":"Point","coordinates":[36.112060546875,-0.03295898255728957],"properties":{"id":"drawing_layer.79c08238-4084-4825-9e76-f018527d45b7"},"crs":{"type":"link","properties":{"href":"http://spatialreference.org/ref/epsg/4326/proj4/","type":"proj4"}}},{"type":"Polygon","coordinates":[[[36.749267578125,0.1867672473697155],[36.6943359375,-0.043945308191354115],[36.99096679687499,-0.043945308191354115],[36.9140625,0.1757809742470755],[36.749267578125,0.1867672473697155]]],"properties":{"id":"drawing_layer.ffa36dfd-5767-4946-890b-f4c0d9c0ff9f"},"crs":{"type":"link","properties":{"href":"http://spatialreference.org/ref/epsg/4326/proj4/","type":"proj4"}}}]}

.. important::

    When pasting the ``geometry`` value from above, ensure that there are no new lines / returns after (i.e. press Backspace after pasting).

12. Reuse Existing Helper Function to Get Time Series
=====================================================

With the parameters properly vetted, you are now ready to call the ``get_time_series_from_image_collection`` function. It should be a fairly straightforward call of the function, mapping the REST parameters to the arguments of the function. You will need to make a few minor changes to the function, however, to accommodate the new ``orient`` option.

1. Refactor the ``get_time_series_from_image_collection`` function in :file:`gee/methods.py` to accept the ``orient`` argument by replacing the function with this new definition:

.. code-block:: python

    def get_time_series_from_image_collection(platform, sensor, product, index_name, scale=30, geometry=None,
                                              date_from=None, date_to=None, reducer='median', orient='df'):
        """
        Derive time series at given geometry.
        """
        time_series = []
        ee_product = EE_PRODUCTS[platform][sensor][product]
        collection_name = ee_product['collection']

        if not isinstance(geometry, geojson.GeometryCollection):
            raise ValueError('Geometry must be a valid GeoJSON GeometryCollection.')

        for geom in geometry.geometries:
            log.debug(f'Computing Time Series for Geometry of Type: {geom.type}')

            try:
                ee_geometry = None
                if isinstance(geom, geojson.Polygon):
                    ee_geometry = ee.Geometry.Polygon(geom.coordinates)
                elif isinstance(geom, geojson.Point):
                    ee_geometry = ee.Geometry.Point(geom.coordinates)
                else:
                    raise ValueError('Only Points and Polygons are supported.')

                if date_from is not None:
                    if index_name is not None:
                        indexCollection = ee.ImageCollection(collection_name) \
                            .filterDate(date_from, date_to) \
                            .select(index_name)
                    else:
                        indexCollection = ee.ImageCollection(collection_name) \
                            .filterDate(date_from, date_to)
                else:
                    indexCollection = ee.ImageCollection(collection_name)

                def get_index(image):
                    if reducer:
                        the_reducer = getattr(ee.Reducer, reducer)()

                    if index_name is not None:
                        index_value = image.reduceRegion(the_reducer, ee_geometry, scale).get(index_name)
                    else:
                        index_value = image.reduceRegion(the_reducer, ee_geometry, scale)

                    date = image.get('system:time_start')
                    index_image = ee.Image().set('indexValue', [ee.Number(date), index_value])
                    return index_image

                index_collection = indexCollection.map(get_index)
                index_collection_agg = index_collection.aggregate_array('indexValue')
                values = index_collection_agg.getInfo()
                log.debug('Values acquired.')
                df = pd.DataFrame(values, columns=['Time', index_name.replace("_", " ")])

                if orient == 'df':
                    time_series.append(df)
                else:
                    time_series.append(df.to_dict(orient=orient))

            except EEException:
                log.exception('An error occurred while attempting to retrieve the time series.')

        log.debug(f'Time Series: {time_series}')
        return time_series

.. note::

    You don't need to worry about updating existing calls of ``get_time_series_from_image_collection``, because the new ``orient`` argument was added at the end of the argument list with a default value that will cause it to behave as it did before the argument was added.

2. Modify the ``get_time_series`` controller in :file:`controllers/rest.py` to call the ``get_time_series_from_image_collection`` function and return the time series in the response object. Replace the ``response_data`` object with the following:

.. code-block:: python

    from django.http import HttpResponseServerError
    from ..gee.methods import get_time_series_from_image_collection


.. code-block:: python
    :emphasize-lines: 1

    try:
        time_series = get_time_series_from_image_collection(
            platform=platform,
            sensor=sensor,
            product=product,
            index_name=index,
            scale=scale,
            geometry=geometry,
            date_from=start_date_str,
            date_to=end_date_str,
            reducer=reducer,
            orient=orient
        )
    except ValueError as e:
        return HttpResponseBadRequest(str(e))
    except Exception:
        log.exception('An unexpected error occurred during execution of get_time_series_from_image_collection.')
        return HttpResponseServerError('An unexpected error occurred. Please review your parameters and try again.')

    # compose response object.
    response_data = {
        'time_series': time_series,
        'parameters': {
            'platform': platform,
            'sensor': sensor,
            'product': product,
            'index': index,
            'start_date': start_date_str,
            'end_date': end_date_str,
            'reducer': reducer,
            'orient': orient,
            'scale': scale,
            'geometry': geometry
        }
    }

    return JsonResponse(response_data)


3. Enable all of the Query parameters in Postman by checking the box next to each with the exception of the ``index`` parameter. Ensure that the values given for the enabled parameters are valid.

4. Press the **Send** button to submit the request and verify that the time series is included in the response object.

13. Test & Verify
=================

1. Use Postman to try different values for each of the parameters. Use some that are valid and others that are not to ensure the validation is working.
2. Switch the method from "GET" to "POST".
3. Uncheck all of the Query parameters in the **Params** tab.
4. Select the **Body** tab and toggle on the **form-data** radio button.
5. Press the **Bulk Edit** link at the right and insert the following:

.. code-block::

    platform:modis
    sensor:terra
    product:temperature
    start_date:2020-02-15
    end_date:2020-04-14
    reducer:mean
    //index:NDVI
    geometry:{"type":"GeometryCollection","geometries":[{"type":"Point","coordinates":[36.112060546875,-0.03295898255728957],"properties":{"id":"drawing_layer.79c08238-4084-4825-9e76-f018527d45b7"},"crs":{"type":"link","properties":{"href":"http://spatialreference.org/ref/epsg/4326/proj4/","type":"proj4"}}},{"type":"Polygon","coordinates":[[[36.749267578125,0.1867672473697155],[36.6943359375,-0.043945308191354115],[36.99096679687499,-0.043945308191354115],[36.9140625,0.1757809742470755],[36.749267578125,0.1867672473697155]]],"properties":{"id":"drawing_layer.ffa36dfd-5767-4946-890b-f4c0d9c0ff9f"},"crs":{"type":"link","properties":{"href":"http://spatialreference.org/ref/epsg/4326/proj4/","type":"proj4"}}}]}
    orient:series
    scale:250

6. Press the **Send** button to ensure the API works as expected with the POST method. The response should look similar to the following:

.. code-block:: json

    {
        "time_series": [
            {
                "Time": "{\"0\":1581724800000,\"1\":1581811200000,\"2\":1581897600000,\"3\":1581984000000,\"4\":1582070400000,\"5\":1582156800000,\"6\":1582243200000,\"7\":1582329600000,\"8\":1582416000000,\"9\":1582502400000,\"10\":1582588800000,\"11\":1582675200000,\"12\":1582761600000,\"13\":1582848000000,\"14\":1582934400000,\"15\":1583020800000,\"16\":1583107200000,\"17\":1583193600000,\"18\":1583280000000,\"19\":1583366400000,\"20\":1583452800000,\"21\":1583539200000,\"22\":1583625600000,\"23\":1583712000000,\"24\":1583798400000,\"25\":1583884800000,\"26\":1583971200000,\"27\":1584057600000,\"28\":1584144000000,\"29\":1584230400000,\"30\":1584316800000,\"31\":1584403200000,\"32\":1584489600000,\"33\":1584576000000,\"34\":1584662400000,\"35\":1584748800000,\"36\":1584835200000,\"37\":1584921600000,\"38\":1585008000000,\"39\":1585094400000,\"40\":1585180800000,\"41\":1585267200000,\"42\":1585353600000,\"43\":1585440000000,\"44\":1585526400000,\"45\":1585612800000,\"46\":1585699200000,\"47\":1585785600000,\"48\":1585872000000,\"49\":1585958400000,\"50\":1586044800000,\"51\":1586131200000,\"52\":1586217600000,\"53\":1586304000000,\"54\":1586390400000,\"55\":1586476800000,\"56\":1586563200000,\"57\":1586649600000,\"58\":1586736000000}",
                "LST Day 1km": "{\"0\":null,\"1\":null,\"2\":15178.0,\"3\":15046.0,\"4\":14882.0,\"5\":null,\"6\":15409.0,\"7\":15030.0,\"8\":null,\"9\":15091.0,\"10\":null,\"11\":null,\"12\":null,\"13\":15470.0,\"14\":15252.0,\"15\":15511.0,\"16\":null,\"17\":null,\"18\":null,\"19\":null,\"20\":15595.0,\"21\":null,\"22\":15197.0,\"23\":null,\"24\":null,\"25\":15024.0,\"26\":14907.0,\"27\":15346.0,\"28\":null,\"29\":15627.0,\"30\":15120.0,\"31\":15024.0,\"32\":null,\"33\":null,\"34\":15139.0,\"35\":15090.0,\"36\":15626.0,\"37\":null,\"38\":15224.0,\"39\":null,\"40\":15013.0,\"41\":null,\"42\":null,\"43\":null,\"44\":null,\"45\":15295.0,\"46\":null,\"47\":15368.0,\"48\":15342.0,\"49\":null,\"50\":15053.0,\"51\":null,\"52\":15189.0,\"53\":null,\"54\":15094.0,\"55\":15107.0,\"56\":15415.0,\"57\":15263.0,\"58\":null}"
            },
            {
                "Time": "{\"0\":1581724800000,\"1\":1581811200000,\"2\":1581897600000,\"3\":1581984000000,\"4\":1582070400000,\"5\":1582156800000,\"6\":1582243200000,\"7\":1582329600000,\"8\":1582416000000,\"9\":1582502400000,\"10\":1582588800000,\"11\":1582675200000,\"12\":1582761600000,\"13\":1582848000000,\"14\":1582934400000,\"15\":1583020800000,\"16\":1583107200000,\"17\":1583193600000,\"18\":1583280000000,\"19\":1583366400000,\"20\":1583452800000,\"21\":1583539200000,\"22\":1583625600000,\"23\":1583712000000,\"24\":1583798400000,\"25\":1583884800000,\"26\":1583971200000,\"27\":1584057600000,\"28\":1584144000000,\"29\":1584230400000,\"30\":1584316800000,\"31\":1584403200000,\"32\":1584489600000,\"33\":1584576000000,\"34\":1584662400000,\"35\":1584748800000,\"36\":1584835200000,\"37\":1584921600000,\"38\":1585008000000,\"39\":1585094400000,\"40\":1585180800000,\"41\":1585267200000,\"42\":1585353600000,\"43\":1585440000000,\"44\":1585526400000,\"45\":1585612800000,\"46\":1585699200000,\"47\":1585785600000,\"48\":1585872000000,\"49\":1585958400000,\"50\":1586044800000,\"51\":1586131200000,\"52\":1586217600000,\"53\":1586304000000,\"54\":1586390400000,\"55\":1586476800000,\"56\":1586563200000,\"57\":1586649600000,\"58\":1586736000000}",
                "LST Day 1km": "{\"0\":14968.8013557598,\"1\":14732.0,\"2\":15140.6162672913,\"3\":14964.0387762783,\"4\":14997.5439551696,\"5\":null,\"6\":15329.096412742,\"7\":15040.9105709928,\"8\":14961.5659903202,\"9\":15247.6460587379,\"10\":15128.6494517054,\"11\":null,\"12\":null,\"13\":15315.9218134749,\"14\":15142.2256710748,\"15\":15489.6098782062,\"16\":null,\"17\":null,\"18\":14830.7316079983,\"19\":null,\"20\":15365.3874342389,\"21\":null,\"22\":15096.8693791135,\"23\":null,\"24\":14571.8987736331,\"25\":14941.6888052079,\"26\":14906.3561937113,\"27\":15206.5296095194,\"28\":null,\"29\":15568.0890033355,\"30\":15302.2537246606,\"31\":15168.7467805083,\"32\":14991.9650580776,\"33\":15031.5642354043,\"34\":14976.2529256142,\"35\":15015.4395296379,\"36\":15419.699948541,\"37\":null,\"38\":15306.6092905512,\"39\":15305.2591368269,\"40\":null,\"41\":null,\"42\":null,\"43\":14921.4426529555,\"44\":null,\"45\":15293.5047969806,\"46\":null,\"47\":15155.7042583175,\"48\":15072.2772985564,\"49\":14963.3847646173,\"50\":14974.3150231811,\"51\":null,\"52\":15099.3012719277,\"53\":null,\"54\":15242.5142541762,\"55\":15089.3998174908,\"56\":15442.3522075961,\"57\":15175.1380971884,\"58\":null}"
            }
        ],
        "parameters": {
            "platform": "modis",
            "sensor": "terra",
            "product": "temperature",
            "index": "LST_Day_1km",
            "start_date": "2020-02-15",
            "end_date": "2020-04-14",
            "reducer": "mean",
            "orient": "series",
            "scale": 250.0,
            "geometry": {
                "type": "GeometryCollection",
                "geometries": [
                    {
                        "type": "Point",
                        "properties": {
                            "id": "drawing_layer.79c08238-4084-4825-9e76-f018527d45b7"
                        },
                        "crs": {
                            "type": "link",
                            "properties": {
                                "href": "http://spatialreference.org/ref/epsg/4326/proj4/",
                                "type": "proj4"
                            }
                        },
                        "coordinates": [
                            36.112061,
                            -0.032959
                        ]
                    },
                    {
                        "type": "Polygon",
                        "properties": {
                            "id": "drawing_layer.ffa36dfd-5767-4946-890b-f4c0d9c0ff9f"
                        },
                        "crs": {
                            "type": "link",
                            "properties": {
                                "href": "http://spatialreference.org/ref/epsg/4326/proj4/",
                                "type": "proj4"
                            }
                        },
                        "coordinates": [
                            [
                                [
                                    36.749268,
                                    0.186767
                                ],
                                [
                                    36.694336,
                                    -0.043945
                                ],
                                [
                                    36.990967,
                                    -0.043945
                                ],
                                [
                                    36.914062,
                                    0.175781
                                ],
                                [
                                    36.749268,
                                    0.186767
                                ]
                            ]
                        ]
                    }
                ]
            }
        }
    }

14. Solution
============

This concludes this portion of the GEE Tutorial. You can view the solution on GitHub at `<https://github.com/tethysplatform/tethysapp-earth_engine/tree/rest-api-solution>`_ or clone it as follows:

.. parsed-literal::

    git clone https://github.com/tethysplatform/tethysapp-earth_engine
    cd tethysapp-earth_engine
    git checkout -b rest-api-solution rest-api-solution-|version|
