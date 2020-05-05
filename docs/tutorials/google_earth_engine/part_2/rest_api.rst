**************
Add a REST API
**************

**Last Updated:** May 2020

In this tutorial you will add a REST API endpoint to the Earth Engine app. This will provide a programmatic access point to the data hosted by your app. Topics covered in this tutorial include:

* REST APIs in Tethys Apps
* Django REST Framework
* Token Authentication
* Controllers in Multiple Files
* Developing REST APIs with Postman

0. Start From Previous Solution (Optional)
==========================================

If you wish to use the previous solution as a starting point:

.. parsed-literal::

    git clone https://github.com/tethysplatform/tethysapp-earth_engine.git
    cd tethysapp-earth_engine
    git checkout -b clip-by-asset-solution clip-by-asset-solution-|version|

1. Reorganize Controller Functions into Separate Files
======================================================

The ``controllers.py`` file is getting quite long...

1. Create a new folder called :file:`controllers` in the :file:`earth_engine` directory with the following new empty Python modules in it:

    * :file:`controllers/`
        * :file:`__init__.py`
        * :file:`home.py`
        * :file:`viewer.py`
        * :file:`rest.py`

    .. note::

        A folder with a file named :file:`__init__.py` is called a Python package.

2. Copy the ``home`` and ``about`` controller functions, with any imports they need into the new :file:`controllers/home.py` module:

.. code-block:: python

    import logging
    from django.shortcuts import render
    from tethys_sdk.permissions import login_required

    log = logging.getLogger(f'tethys.apps.{__name__}')


    @login_required()
    def home(request):
        """
        Controller for the app home page.
        """
        context = {}
        return render(request, 'earth_engine/home.html', context)


    @login_required()
    def about(request):
        """
        Controller for the app about page.
        """
        context = {}
        return render(request, 'earth_engine/about.html', context)

3. Copy the ``viewer``, ``get_image_collection``, ``get_time_series_plot``, and ``handle_shapefile_upload`` controller functions with any imports they need into the new :file:`controllers/viewer.py` module:

.. code-block:: python

    import datetime as dt
    import geojson
    import logging
    from django.http import HttpResponseRedirect, HttpResponseNotAllowed, JsonResponse
    from django.shortcuts import render
    from simplejson import JSONDecodeError
    from tethys_sdk.gizmos import SelectInput, DatePicker, Button, MapView, MVView, PlotlyView, MVDraw
    from tethys_sdk.permissions import login_required
    from tethys_sdk.workspaces import user_workspace
    from ..gee.methods import get_boundary_fc_props_for_user, get_image_collection_asset, \
        get_time_series_from_image_collection, upload_shapefile_to_gee
    from ..gee.products import EE_PRODUCTS
    from ..helpers import generate_figure, compute_dates_for_product, find_shapefile, \
        prep_boundary_dir, write_boundary_shapefile

    log = logging.getLogger(f'tethys.apps.{__name__}')

.. code-block:: python

    @login_required()
    @user_workspace
    def viewer(request, user_workspace):
        """
        Controller for the app home page.
        """

        ...  # Code not shown for brevity

        return render(request, 'earth_engine/viewer.html', context)


    @login_required()
    def get_image_collection(request):
        """
        Controller to handle image collection requests.
        """

        ...  # Code not shown for brevity

        return JsonResponse(response_data)


    @login_required()
    def get_time_series_plot(request):

        ...  # Code not shown for brevity

        return render(request, 'earth_engine/plot.html', context)

    def handle_shapefile_upload(request, user_workspace):
        """
        Uploads shapefile to Google Earth Engine as an Asset.

        Args:
            request (django.Request): the request object.
            user_workspace (tethys_sdk.workspaces.Workspace): the User workspace object.

        Returns:
            str: Error string if errors occurred.
        """
        ... # Code not shown for brevity


4. Update the ``UrlMaps`` in :file:`app.py` to point to the new locations of the controllers:

.. code-block:: python
    :emphasize-lines: 11, 16, 21, 26, 31

    def url_maps(self):
        """
        Add controllers
        """
        UrlMap = url_map_maker(self.root_url)

        url_maps = (
            UrlMap(
                name='home',
                url='earth-engine',
                controller='earth_engine.controllers.home.home'
            ),
            UrlMap(
                name='viewer',
                url='earth-engine/viewer',
                controller='earth_engine.controllers.viewer.viewer'
            ),
            UrlMap(
                name='get_image_collection',
                url='earth-engine/viewer/get-image-collection',
                controller='earth_engine.controllers.viewer.get_image_collection'
            ),
            UrlMap(
                name='get_time_series_plot',
                url='earth-engine/viewer/get-time-series-plot',
                controller='earth_engine.controllers.viewer.get_time_series_plot'
            ),
            UrlMap(
                name='about',
                url='earth-engine/about',
                controller='earth_engine.controllers.home.about'
            ),
        )

        return url_maps

5. Delete the old :file:`controllers.py` file.

6. Navigate to `<http://localhost:8000/apps/earth-engine/>`_ and verify that the app functions as it did before the change.

2. Create New UrlMap and Controller for REST API Endpoint
=========================================================

1. Create a new controller function named ``get_time_series`` in :file:`controllers/rest.py` with the following contents:

.. code-block:: python

    import logging
    from django.http import JsonResponse
    from rest_framework.authentication import TokenAuthentication
    from rest_framework.decorators import api_view, authentication_classes

    log = logging.getLogger(f'tethys.apps.{__name__}')


    @api_view(['GET', 'POST'])
    @authentication_classes((TokenAuthentication,))
    def get_time_series(request):
        """
        Controller for the app home page.
        """
        response_data = {
            "detail": "Hello, World!"
        }
        return JsonResponse(response_data)

2. Add a new ``UrlMap`` for the ``get_time_series`` controller to :file:`app.py`:

.. code-block:: python
    :emphasize-lines: 33-37

    def url_maps(self):
        """
        Add controllers
        """
        UrlMap = url_map_maker(self.root_url)

        url_maps = (
            UrlMap(
                name='home',
                url='earth-engine',
                controller='earth_engine.controllers.home.home'
            ),
            UrlMap(
                name='viewer',
                url='earth-engine/viewer',
                controller='earth_engine.controllers.viewer.viewer'
            ),
            UrlMap(
                name='get_image_collection',
                url='earth-engine/viewer/get-image-collection',
                controller='earth_engine.controllers.viewer.get_image_collection'
            ),
            UrlMap(
                name='get_time_series_plot',
                url='earth-engine/viewer/get-time-series-plot',
                controller='earth_engine.controllers.viewer.get_time_series_plot'
            ),
            UrlMap(
                name='about',
                url='earth-engine/about',
                controller='earth_engine.controllers.home.about'
            ),
            UrlMap(
                name='rest_get_time_series',
                url='earth-engine/api/get-time-series',
                controller='earth_engine.controllers.rest.get_time_series'
            )
        )

        return url_maps

3. Navigate to `<http://localhost:8000/apps/earth-engine/api/get-time-series/>`_. You should see an API page that is auto generated by the `Django REST Framework <https://www.django-rest-framework.org/>`_ titled **Get Time Series**. The page should display an *HTTP 401 Unauthorized* error and display a result object with detail "Authentication credentials were not provided."

3. Test with Postman Application
================================

Testing REST APIs is most easily done with a REST client like Postman.

1. If you have not done so already, `download and install the Postman app <https://www.postman.com/>`_ and then launch it.

2. In Postman click on the **New** and select Collection.

3. Name the collection "Earth Engine App API" and press the **Create** button.

4. Right-click on the new *Earth Engine App API* collection or click on it's dot menu and select **Add Request**.

5. Name the new request "get-time-series" and press the **Save to Earth Engine App API** button.

6. From the menu on the left, expand the *Earth Engine App API* collection and click on the *get-time-series* request to open it in a new tab.

7. Select **GET** as the method and enter "http://localhost:8000/apps/earth-engine/api/get-time-series/" in the URL field.

8. Press the **Save** button to save changes.

9. Press the **Send** button. You should see the same response object as before with the "Authentication credentials were not provided." message.

4. Add Token Authorization Headers to Postman Request
=====================================================

1. Navigate to `<http://localhost:8000/>` and sign in if necessary.

2. Click on the button with your username on it in the top-right-hand corner of the page to access your user profile.

3. Copy the value of the API Key.

4. In Postman, click on the Authorization tab, just under the URL field.

5. Select "API Key" as the **TYPE** and enter the "Authorization" for the **Key** and "Token <your token>" for the value (replace ``<your token>`` with the token you copied).

6. Press the **Send** button again. This time the request should be sent with the proper authorization token. You should see a response object with the "Hello, World!" message.

7. Press the **Save** button to save your changes to the Postman request.

5. Define Parameters for REST API
=================================

1. Update the ``get_time_series`` controller in :file:`controllers/rest.py` as follows:

.. code-block:: python

    @api_view(['GET', 'POST'])
    @authentication_classes((TokenAuthentication,))
    def get_time_series(request):
        """
        Controller for the app home page.
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
                'geometry': geometry
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

4. Press the **Send** button and verify that the parameters are returned in the response object.

6. Validate Platform, Sensor, Product, and Index
================================================

1. Modify the ``get_time_series`` controller in :file:`controllers/rest.py` to add validation for the ``platform``, ``sensor``, ``product``, and ``index`` parameters as follows:

.. code-block:: python

    from django.http import JsonResponse, HttpResponseBadRequest
    from tethysapp.earth_engine.gee.products import EE_PRODUCTS

.. code-block:: python
    :emphasize-lines: 25-70

    @api_view(['GET', 'POST'])
    @authentication_classes((TokenAuthentication,))
    def get_time_series(request):
        """
        Controller for the app home page.
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
                'geometry': geometry
            }
        }

        return JsonResponse(response_data)

2. In Postman, select the **Params** tab if not already active and press the **Key-Value Edit** link at the top-right corner of the tab.

3. Uncheck all of the parameters so that they are not included in the request.

4. Press the **Send** button and verify that the status code *400 Bad Request* is returned (see top-right side of the response section) and the validation message for the ``platform`` parameter is returned.

5. Add the ``platform`` parameter to the request by checking the box next to it.

6. Press the **Send** button and verify that the status code *400 Bad Request* is returned (see top-right side of the response section) and the validation message for the ``sensor`` parameter is returned.

7. Change the value of the ``platform`` parameter to "landsat" or "sentinel" and verify that the validation message for the ``sensor`` parameter lists the appropriate sensors.

8. Repeat this process, adding first the ``product`` parameter and then the ``index parameter`` to confirm that the validation logic is working as expected.

7. Validate Dates
=================

There is logic that already exists in the ``viewer`` controller that you can use to validate the date parameters in our REST API function. However, you should avoid copying code to prevent duplicating bugs and make the app easier to maintain. Instead, we'll generalize the bit of code from the ``viewer`` controller into a helper function and then use that function in both the ``viewer`` controller and the ``get_time_series`` controller.

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

2. Refactor the ``viewer`` controller in :file:`controllers/viewer.py`` to use the new ``compute_dates_for_product`` helper function. Replace all of the previous date logic:

.. code-block:: python

    from ..helpers import handle_shapefile_upload, generate_figure, compute_dates_for_product

.. code-block:: python
    :emphasize-lines: 17-18, 26-28, 39-41

    @login_required()
    @user_workspace
    def viewer(request, user_workspace):
        """
        Controller for the app home page.
        """
        ...  # Code not shown for brevity

        plot_button = Button(
            name='load_plot',
            display_text='Plot AOI',
            style='default',
            attributes={'id': 'load_plot'}
        )

        # Get initial default dates and date ranges for date picker controls
        first_product_dates = compute_dates_for_product(first_product)

        start_date = DatePicker(
            name='start_date',
            display_text='Start Date',
            format='yyyy-mm-dd',
            start_view='decade',
            today_button=True,
            today_highlight=True,
            start_date=first_product_dates['beg_valid_date_range'],
            end_date=first_product_dates['end_valid_date_range'],
            initial=first_product_dates['default_start_date'],
            autoclose=True
        )

        end_date = DatePicker(
            name='end_date',
            display_text='End Date',
            format='yyyy-mm-dd',
            start_view='decade',
            today_button=True,
            today_highlight=True,
            start_date=first_product_dates['beg_valid_date_range'],
            end_date=first_product_dates['end_valid_date_range'],
            initial=first_product_dates['default_end_date'],
            autoclose=True
        )

        # Build reducer method control
        reducer_select = SelectInput(
            name='reducer',
            display_text='Reduction Method',
            options=(
                ('Median', 'median'),
                ('Mosaic', 'mosaic'),
                ('Mode', 'mode'),
                ('Mean', 'mean'),
                ('Minimum', 'min'),
                ('Maximum', 'max'),
                ('Sum', 'sum'),
                ('Count', 'count'),
                ('Product', 'product'),
            )
        )
       ...  # Code not shown for brevity

3. Modify the ``get_time_series`` controller in :file:`controllers/rest.py` to add validation for the ``start_date`` and ``end_date`` parameters as follows:

.. code-block:: python

    import datetime as dt
    from tethysapp.earth_engine.helpers import compute_dates_for_product

.. code-block:: python

    @api_view(['GET', 'POST'])
    @authentication_classes((TokenAuthentication,))
    def get_time_series(request):
        """
        Controller for the app home page.
        """
        ...  # Code not shown for brevity
        # get valid dates for selected product
        product_dates = compute_dates_for_product(selected_product)

        # assign default start date if not provided
        if not start_date_str:
            start_date_str = product_dates['default_start_date']

        # assign default start date if not provided
        if not end_date_str:
            end_date_str = product_dates['default_end_date']

        # convert to datetime objects for validation
        start_date_dt = dt.datetime.strptime(start_date_str, '%Y-%m-%d')
        end_date_dt = dt.datetime.strptime(end_date_str, '%Y-%m-%d')
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
                'geometry': geometry
            }
        }

        return JsonResponse(response_data)


4. Use the technique from steps 6.5 - 6.8 to test the ``start_date`` and ``end_date`` parameters using Postman.

5. Also test different values for dates to test the following scenarios:

    * ``start_date`` == ``end_date``
    * ``start_date`` > ``end_date``
    * ``start_date`` < ``end_date``
    * ``start_date`` outside of valid range of selected product (see :file:`gee/products.py`)
    * ``end_date`` outside of valid range of selected product (see :file:`gee/products.py`)
    * ``start_date`` and ``end_date`` outside of valid range of selected product (see :file:`gee/products.py`)
    * Incorrect date format given for either date parameter

8. Validate Reducer, Orient, and Scale
======================================

1. Modify the ``get_time_series`` controller in :file:`controllers/rest.py` to add validation for the ``reducer``, ``orient``, and ``scale`` parameters as follows:

.. code-block:: python

    @api_view(['GET', 'POST'])
    @authentication_classes((TokenAuthentication,))
    def get_time_series(request):
        """
        Controller for the app home page.
        """
        ...  # Code not shown for brevity
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
                'geometry': geometry
            }
        }

        return JsonResponse(response_data)


2. Use the technique from steps 6.5 - 6.8 to test the ``reducer``, ``orient``, and ``scale`` parameters using Postman.


9. Validate Geometry
====================

1. Modify the ``get_time_series`` controller in :file:`controllers/rest.py` to add validation for the ``geometry`` parameter as follows:

.. code-block:: python

    import geojson
    from simplejson import JSONDecodeError

.. code-block:: python
    :emphasize-lines: 1

    @api_view(['GET', 'POST'])
    @authentication_classes((TokenAuthentication,))
    def get_time_series(request):
        """
        Controller for the app home page.
        """
        ...  # Code not shown for brevity
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
                'geometry': geometry
            }
        }

        return JsonResponse(response_data)

2. Use the technique from steps 6.5 - 6.8 to test the ``geometry`` parameter using Postman.

10. Reuse Existing Helper Function to Get Time Series
=====================================================

1. Refactor the ``get_time_series_from_image_collection`` function in :file:`gee/methods.py` to accept the ``orient`` argument by replacing the function with this new definition:

2. Modify the ``get_time_series`` controller in :file:`controllers/rest.py` to call the ``get_time_series_from_image_collection`` function and return the time series in the response object:

.. code-block:: python

    from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseServerError
    from tethysapp.earth_engine.gee.methods import get_time_series_from_image_collection


.. code-block:: python
    :emphasize-lines: 1

    @api_view(['GET', 'POST'])
    @authentication_classes((TokenAuthentication,))
    def get_time_series(request):
        """
        Controller for the app home page.
        """
        ...  # Code not shown for brevity
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
                'geometry': geometry
            }
        }

        return JsonResponse(response_data)


3. Enable all of the Query parameters in Postman by checking the box next to each with the exception of the ``index`` parameter.

4. Press the **Send** button to submit the request and verify that the time series is included in the response object.

11. Test & Verify
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

6. Press the **Send** button to ensure the API works as expected with the POST method.

12. Solution
============

This concludes this portion of the GEE Tutorial. You can view the solution on GitHub at `<https://github.com/tethysplatform/tethysapp-earth_engine/tree/rest-api-solution-solution-3.0>`_ or clone it as follows:

.. parsed-literal::

    git clone https://github.com/tethysplatform/tethysapp-earth_engine.git
    cd tethysapp-earth_engine
    git checkout -b rest-api-solution-solution rest-api-solution-solution-|version|