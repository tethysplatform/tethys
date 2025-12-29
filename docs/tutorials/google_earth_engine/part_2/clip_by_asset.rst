*************
Clip by Asset
*************

**Last Updated:** July 2024

In this tutorial you will use the shapefile uploaded using the file upload form to clip the dataset imagery. This will be done by uploading the shapefile to Google Earth Engine as an asset. Then the map will be reconfigured to check for the asset and clip the imagery if it exists. It will also use the bounding box of the asset to set the default map extent. The following topics will be reviewed in this tutorial:

* `Google Earth Engine Assets <https://developers.google.com/earth-engine/guides/manage_assets>`_
* Clipping Google Earth Engine Imagery

.. figure:: ../../../images/tutorial/gee/clip_by_asset.png
    :width: 800px
    :align: center

0. Start From Previous Solution (Optional)
==========================================

If you wish to use the previous solution as a starting point:

.. parsed-literal::

    git clone https://github.com/tethysplatform/tethysapp-earth_engine
    cd tethysapp-earth_engine
    git checkout -b file-upload-solution file-upload-solution-|version|


1. Stub out New Method for Uploading Shapefiles to GEE
======================================================

In this step you will stub out a new GEE method called ``upload_shapefile_to_gee`` that will be responsible for uploading the shapefile provided by the user as an asset to GEE.

1. Create new ``upload_shapefile_to_gee`` function in :file:`gee/methods.py` with the following contents:

.. code-block:: python

    def upload_shapefile_to_gee(user, shp_file):
        """
        Upload a shapefile to Google Earth Engine as an asset.

        Args:
            user (django.contrib.auth.User): the request user.
            shp_file (shapefile.Reader): A shapefile reader object.
        """
        print(user.username)
        print(shp_file)

2. Import the new ``upload_shapefile_to_gee`` function and call it in ``handle_shapefile_upload`` function in :file:`helpers.py` after validating the shapefile upload. Also add an additional ``except`` clause to handle any uncaught Google Earth Engine errors:

.. code-block:: python

    import logging
    import ee
    from .gee.methods import upload_shapefile_to_gee

    log = logging.getLogger(f'tethys.apps.{__name__}')

.. code-block:: python
    :emphasize-lines: 51-52, 57-60

    def handle_shapefile_upload(request, user_media):
        """
        Uploads shapefile to Google Earth Engine as an Asset.

        Args:
            request (django.Request): the request object.
            user_media (tethys_sdk.paths.TethysPath): the User media object.

        Returns:
            str: Error string if errors occurred.
        """
        # Write file to temp for processing
        uploaded_file = request.FILES['boundary-file']

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_zip_path = os.path.join(temp_dir, 'boundary.zip')

            # Use with statements to ensure opened files are closed when done
            with open(temp_zip_path, 'wb') as temp_zip:
                for chunk in uploaded_file.chunks():
                    temp_zip.write(chunk)

            try:
                # Extract the archive to the temporary directory
                with zipfile.ZipFile(temp_zip_path) as temp_zip:
                    temp_zip.extractall(temp_dir)

            except zipfile.BadZipFile:
                # Return error message
                return 'You must provide a zip archive containing a shapefile.'

            # Verify that it contains a shapefile
            try:
                # Find a shapefile in directory where we extracted the archive
                shapefile_path = find_shapefile(temp_dir)

                if not shapefile_path:
                    return 'No Shapefile found in the archive provided.'

                with shapefile.Reader(shapefile_path) as shp_file:
                    # Check type (only Polygon supported)
                    if shp_file.shapeType != shapefile.POLYGON:
                        return 'Only shapefiles containing Polygons are supported.'

                    # Setup user media directory for storing shapefile
                    media_dir = prep_boundary_dir(user_media.path)

                    # Write the shapefile to the media directory
                    write_boundary_shapefile(shp_file, media_dir)

                    # Upload shapefile as Asset in GEE
                    upload_shapefile_to_gee(request.user, shp_file)

            except TypeError:
                return 'Incomplete or corrupted shapefile provided.'

            except ee.EEException:
                msg = 'An unexpected error occurred while uploading the shapefile to Google Earth Engine.'
                log.exception(msg)
                return msg

3. Navigate to `<http://localhost:8000/apps/earth-engine/viewer/>`_ and upload the :file:`USA_simplified.zip`. Verify that ``upload_shapefile_to_gee`` is called by noting the statements it prints to the terminal where Tethys is running.

2. Convert Shapefile to ee.FeatureCollection
============================================

The first step to uploading the shapefile as an asset is to convert it to an ``ee.FeatureCollection``. However, ``ee`` API does not provide a way to create an ``ee.FeatureCollection`` directly from a shapefile. As an intermediate step, the shapefile will be converted first to GeoJSON, which can then be used to create the ``ee.FeatureCollection``.

1. Update the ``upload_shapefile_to_gee`` function in :file:`gee/methods.py` to convert the uploaded shapefile to GeoJSON:

.. code-block:: python
    :emphasize-lines: 9-24

    def upload_shapefile_to_gee(user, shp_file):
        """
        Upload a shapefile to Google Earth Engine as an asset.

        Args:
            user (django.contrib.auth.User): the request user.
            shp_file (shapefile.Reader): A shapefile reader object.
        """
        features = []
        fields = shp_file.fields[1:]
        field_names = [field[0] for field in fields]

        # Convert Shapefile to ee.Features
        for record in shp_file.shapeRecords():
            # First convert to geojson
            attributes = dict(zip(field_names, record.record))
            geojson_geom = record.shape.__geo_interface__
            geojson_feature = {
                'type': 'Feature',
                'geometry': geojson_geom,
                'properties': attributes
            }

            print(geojson_feature)

2. Navigate to `<http://localhost:8000/apps/earth-engine/viewer/>`_ and upload the :file:`USA_simplified.zip`. Verify that the GeoJSON is being printed to the terminal where Tethys is running.

3. Update the ``upload_shapefile_to_gee`` function in :file:`gee/methods.py` to convert create ``ee.Features`` and an ``ee.FeatureCollection`` from the GeoJSON:

.. code-block:: python
    :emphasize-lines: 24-28

    def upload_shapefile_to_gee(user, shp_file):
        """
        Upload a shapefile to Google Earth Engine as an asset.

        Args:
            user (django.contrib.auth.User): the request user.
            shp_file (shapefile.Reader): A shapefile reader object.
        """
        features = []
        fields = shp_file.fields[1:]
        field_names = [field[0] for field in fields]

        # Convert Shapefile to ee.Features
        for record in shp_file.shapeRecords():
            # First convert to geojson
            attributes = dict(zip(field_names, record.record))
            geojson_geom = record.shape.__geo_interface__
            geojson_feature = {
                'type': 'Feature',
                'geometry': geojson_geom,
                'properties': attributes
            }

            # Create ee.Feature from geojson (this is the Upload, b/c ee.Feature is a server object)
            features.append(ee.Feature(geojson_feature))

        feature_collection = ee.FeatureCollection(features)
        print(feature_collection)

4. Navigate to `<http://localhost:8000/apps/earth-engine/viewer/>`_ and upload the :file:`USA_simplified.zip`. Verify that the new ``ee.FeatureCollection`` is printed to the terminal where Tethys is running.

3. Export the New ee.FeatureCollection to an Asset
==================================================

Now that the shapefile has been converted to an ``ee.FeatureCollection``, it can be exported as a Google Earth Engine table asset (see:  `Importing Table Data - Uploading a Shapefile <https://developers.google.com/earth-engine/guides/table_upload>`_). Remember that ``ee`` objects are server objects, which means the features are already on the server. Exporting the ``ee.FeatureCollection`` as an asset persists it to storage in the GEE cloud infrastructure so that you can use it again later without needing to upload it again. Similar to when the shapefile was written to the user's media directory, several helper functions will also be created to manage the folder where the asset will be written.

1. The ``get_asset_dir_for_user`` function will create a folder for the user and return the path. It will make use of the ``get_earth_engine_credentials_path`` function to find the credentials file with information on your Earth Engine account and project. 
Create two new functions: ``get_earth_engine_credentials_path``, and  ``get_asset_dir_for_user``, both in :file:`gee/methods.py` with the following contents:

.. code-block:: python

    import os
    import platform
    import json

.. code-block:: python

    def get_earth_engine_credentials_path():
        """Returns the full path to the Earth Engine credentials file.
        
        Compatible with both Linux/MacOS and Windows.
        """
        if platform.system() in ["Linux", "Darwin"]:
            return os.path.expanduser("~/.config/earthengine/credentials")

        elif platform.system() == "Windows":
            user_profile = os.environ["USERPROFILE"]
            return os.path.join(user_profile, ".config", "earthengine", "credentials")

        else:
            raise OSError("Unsupported operating system.")

.. code-block:: python

    def get_asset_dir_for_user(user):
        """
        Get a unique asset directory for given user.

        Args:
            user (django.contrib.auth.User): the request user.

        Returns:
            str: asset directory path for given user.
        """
        asset_roots = ee.batch.data.getAssetRoots()
        if len(asset_roots) < 1:
            # Find the Earth Engine credentials file path
            credentials_path = get_earth_engine_credentials_path()
            try:
                with open(credentials_path) as f:
                    credentials = json.load(f)
                    # Get the project ID from the credentials
                    project_id = credentials.get("project", None)
                    if not project_id:
                        raise ValueError('Project ID not found in credentials.')
            except FileNotFoundError:
                raise ValueError('Credentials file not found.')
            
            asset_path = f"projects/{project_id}/assets/tethys"
            # Create the asset directory
            ee.batch.data.createAsset({
                'type': 'Folder',
                'name': asset_path
            })

            asset_roots = ee.batch.data.getAssetRoots()

        # Prepare asset directory paths
        asset_root_dir = asset_roots[0]['id']
        earth_engine_root_dir = asset_root_dir + "/earth_engine_app"
        user_root_dir = earth_engine_root_dir + f"/{user.username}"

        # Create earth engine directory, will raise exception if it already exists
        try:
            ee.batch.data.createAsset({
                'type': 'Folder',
                'name': earth_engine_root_dir
            })
        except EEException as e:
            if 'Cannot overwrite asset' not in str(e):
                raise e

        # Create user directory, will raise exception if it already exists
        try:
            ee.batch.data.createAsset({
                'type': 'Folder',
                'name': user_root_dir
            })
        except EEException as e:
            if 'Cannot overwrite asset' not in str(e):
                raise e

        return user_root_dir


2. The ``get_user_boundary_path`` function determines the path to the boundary asset for a given user. Create a new ``get_user_boundary_path`` function in :file:`gee/methods.py` with the following contents:

.. code-block:: python

    def get_user_boundary_path(user):
        """
        Get a unique path for the user boundary asset.

        Args:
            user (django.contrib.auth.User): the request user.

        Returns:
            str: the unique path for the user boundary asset.
        """
        user_asset_dir = get_asset_dir_for_user(user)
        user_boundary_asset_path = user_asset_dir + '/boundary'
        return user_boundary_asset_path

3. Update the ``upload_shapefile_to_gee`` function in :file:`gee/methods.py` to call the new ``get_user_boundary_path`` function and then export the ``ee.FeatureCollection`` to an asset at that path: (no try/except)

.. code-block:: python
    :emphasize-lines: 29-40

    def upload_shapefile_to_gee(user, shp_file):
        """
        Upload a shapefile to Google Earth Engine as an asset.

        Args:
            user (django.contrib.auth.User): the request user.
            shp_file (shapefile.Reader): A shapefile reader object.
        """
        features = []
        fields = shp_file.fields[1:]
        field_names = [field[0] for field in fields]

        # Convert Shapefile to ee.Features
        for record in shp_file.shapeRecords():
            # First convert to geojson
            attributes = dict(zip(field_names, record.record))
            geojson_geom = record.shape.__geo_interface__
            geojson_feature = {
                'type': 'Feature',
                'geometry': geojson_geom,
                'properties': attributes
            }

            # Create ee.Feature from geojson (this is the Upload, b/c ee.Feature is a server object)
            features.append(ee.Feature(geojson_feature))

        feature_collection = ee.FeatureCollection(features)

        # Get unique folder for each user to story boundary asset
        user_boundary_asset_path = get_user_boundary_path(user)
        print(user_boundary_asset_path)

        # Export ee.Feature to ee.Asset
        task = ee.batch.Export.table.toAsset(
            collection=feature_collection,
            description='uploadToTableAsset',
            assetId=user_boundary_asset_path
        )

        task.start()

.. tip:: 

    You may need to manually add these empty folders to your assets. In the Google Earth Engine code editor, navigate to the **Assets** tab in the top-left pane of the code editor and create a new folder named  **users**, then another named **earth_engine_app**. Then, simply drag the **earth_engine_app** folder into the **users** folder. 

4. Navigate to `<http://localhost:8000/apps/earth-engine/viewer/>`_ and upload the :file:`USA_simplified.zip`. Verify that the path returned from ``get_user_boundary_path`` is printed to the terminal where Tethys is running.

    .. warning::

        If you have already uploaded an asset, doing so again will fail because we haven't handled the case where the file already exists (see Step 3.7). Either manually delete the asset at `<https://code.earthengine.google.com/>`_ or skip to step 3.8 for the implementation that handles this issue.

5. Navigate to `<https://code.earthengine.google.com/>`_ and select the **Tasks** tab in the top-right pane of the code editor. Verify that a new ``uploadToTableAsset`` task is/was running.

6. Once the ``uploadToTableAsset`` task is complete, select the **Assets** tab in the top-left pane of the code editor and verify that there is a new asset named **boundary** at the path that was printed to the terminal in step 3.4.

    .. tip::

        If the new asset does not appear, try pressing the refresh button.

7. Navigate to `<http://localhost:8000/apps/earth-engine/viewer/>`_ and upload the :file:`USA_simplified.zip` again. The ``uploadToTableAsset`` task in the Google Earth Engine code editor should fail, because Google Earth Engine won't let you overwrite a file that already exists when exporting an asset.

8. Update the ``upload_shapefile_to_gee`` function in :file:`gee/methods.py` to delete the asset before exporting to asset. This will fail if there is no asset there (the first time), so handle with a ``try-except``: (with try/except this time)

.. code-block:: python
    :emphasize-lines: 32-39

    def upload_shapefile_to_gee(user, shp_file):
        """
        Upload a shapefile to Google Earth Engine as an asset.

        Args:
            user (django.contrib.auth.User): the request user.
            shp_file (shapefile.Reader): A shapefile reader object.
        """
        features = []
        fields = shp_file.fields[1:]
        field_names = [field[0] for field in fields]

        # Convert Shapefile to ee.Features
        for record in shp_file.shapeRecords():
            # First convert to geojson
            attributes = dict(zip(field_names, record.record))
            geojson_geom = record.shape.__geo_interface__
            geojson_feature = {
                'type': 'Feature',
                'geometry': geojson_geom,
                'properties': attributes
            }

            # Create ee.Feature from geojson (this is the Upload, b/c ee.Feature is a server object)
            features.append(ee.Feature(geojson_feature))

        feature_collection = ee.FeatureCollection(features)

        # Get unique folder for each user to story boundary asset
        user_boundary_asset_path = get_user_boundary_path(user)

        # Overwrite an existing asset with this name by deleting it first
        try:
            ee.batch.data.deleteAsset(user_boundary_asset_path)
        except EEException as e:
            # Nothing to delete, so pass
            if 'Asset not found' not in str(e) and 'does not exist' not in str(e):
                log.exception('Encountered an unhandled EEException.')
                raise e

        # Export ee.Feature to ee.Asset
        task = ee.batch.Export.table.toAsset(
            collection=feature_collection,
            description='uploadToTableAsset',
            assetId=user_boundary_asset_path
        )

        task.start()

9. Navigate to `<http://localhost:8000/apps/earth-engine/viewer/>`_ and upload the :file:`USA_simplified.zip` again. Verify that no error is shown this time.

10. Navigate to `<https://code.earthengine.google.com/>`_ after successfully uploading the shapefile. Verify that a new ``uploadToTableAsset`` task is running and that the previous **boundary** asset has been removed. Once the ``uploadToTableAsset`` job completes, the asset should once again be shown in the assets tab.

4. Use Boundary Asset to Clip Images
====================================

In this step you will modify the ``get_image_collection_asset`` method to attempt to retrieve the boundary asset and use it to clip the boundary if it exists.

1. The ``get_boundary_fc_for_user`` will retrieve the boundary asset and attempt to convert it to an ``ee.FeatureCollection``. If it succeeds, it will return the ``ee.FeatureCollection``, if it fails, the boundary asset likely has not been created so it will return ``None``. Create a new ``get_boundary_fc_for_user`` function in :file:`gee/methods.py` with the following contents:

.. code-block:: python

    def get_boundary_fc_for_user(user):
        """
        Get the boundary FeatureClass for the given user if it exists.

        Args:
            user (django.contrib.auth.User): the request user.

        Returns:
            ee.FeatureCollection: boundary feature collection or None
        """
        try:
            boundary_path = get_user_boundary_path(user)
            # If no boundary exists for the user, an exception occur when calling this and clipping will skipped
            ee.batch.data.getAsset(boundary_path)
            # Add the clip option
            fc = ee.FeatureCollection(boundary_path)
            return fc
        except EEException:
            pass

        return None

2. Modify the ``get_image_collection_asset`` function in :file:`gee/methods.py` to call the new ``get_boundary_fc_for_user`` function and clip the imagery if something is returned. Also add the ``request`` as an argument as this is needed to get the current user:

.. code-block:: python
    :emphasize-lines: 1, 34-38

    def get_image_collection_asset(request, platform, sensor, product, date_from=None, date_to=None, reducer='median'):
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

            # Attempt to clip the image by the boundary provided by the user
            clip_features = get_boundary_fc_for_user(request.user)

            if clip_features:
                ee_collection = ee_collection.clipToCollection(clip_features)

            tile_url = image_to_map_id(ee_collection, vis_params)

            return tile_url

        except EEException:
            log.exception('An error occurred while attempting to retrieve the image collection asset.')

3. Modify ``get_image_collection`` controller in :file:`controllers.py` to call ``get_image_collection_asset`` with the ``request`` as an additional argument:

.. code-block:: python
    :emphasize-lines: 22

    @controller(url='viewer/get-image-collection')
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
                request=request,
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

4. Navigate to `<http://localhost:8000/apps/earth-engine/viewer/>`_ and wait a moment before loading a dataset of your choice. Verify that the imagery has been clipped to the United States. You'll need to manually pan and zoom to the U.S. to see the imagery.

5. Use Boundary Asset for Map Extents
=====================================

In this step you will modify the ``MapView`` on the Viewer page to use the extents of the boundary asset as the default map extents. If the user has not uploaded a boundary, the boundary asset will not exist, so the ``MapView`` will be changed to default to world extents.

1. The ``get_boundary_fc_props_for_user`` method is responsible for determining various properties about the boundary ``ee.FeatureCollection`` that will be used by the ``MapView``. These properties include the ``bounding_box``, ``centroid``, and ``zoom`` needed to frame the features when the view is centered on the centroid. Create a new ``get_boundary_fc_props_for_user`` function in :file:`gee/methods.py` with the following contents:

.. code-block:: python

    import math

.. code-block:: python

    def get_boundary_fc_props_for_user(user):
        """
        Get various properties of the boundary FeatureCollection.
        Args:
            user (django.contrib.auth.User): Get the properties of the boundary uploaded by this user.

        Returns:
            dict<zoom,bbox,centroid>: Dictionary containing the centroid and bounding box of the boundary and the approximate OpenLayers zoom level to frame the boundary around the centroid. Empty dictionary if no boundary FeatureCollection is found for the given user.
        """
        fc = get_boundary_fc_for_user(user)

        if not fc:
            return dict()

        # Compute bounding box
        bounding_rect = fc.geometry().bounds().getInfo()
        bounding_coords = bounding_rect.get('coordinates')[0]

        # Derive bounding box from two corners of the bounding rectangle
        bbox = [bounding_coords[0][0], bounding_coords[0][1], bounding_coords[2][0], bounding_coords[2][1]]

        # Get centroid
        centroid = fc.geometry().centroid().getInfo()

        # Compute length diagonal of bbox for zoom calculation
        diag = math.sqrt((bbox[0] - bbox[2])**2 + (bbox[1] - bbox[3])**2)

        # Found the diagonal length and zoom level for US and Kenya boundaries
        # Used equation of a line to develop the relationship between zoom and diagonal of bounding box
        zoom = round((-0.0701 * diag) + 8.34, 0)

        # The returned ee.FeatureClass properties
        fc_props = {
            'zoom': zoom,
            'bbox': bbox,
            'centroid': centroid.get('coordinates')
        }

        return fc_props

.. note::

    The ``zoom`` is derived from an overly simplistic analysis on two countries of different size. A boundary polygon for each country was uploaded and the diagonal distance across the bounding box was calculated for each country using the distance formula. The zoom level that framed each country was also noted. A linear equation was developed using the equation of a line and the points formed by the computed diagonal and zoom level. This equation is likely not very robust, but it works as a good first pass.

2. Use the ``get_boundary_fc_props_for_user`` function to get the bounding box and zoom level to use for the ``MapView``. Replace the definition of the ``MapView`` in the ``viewer`` controller in :file:`controllers.py` with the following:

.. code-block:: python

    from .gee.methods import get_boundary_fc_props_for_user

.. code-block:: python
    :emphasize-lines: 1-2, 11, 23-24

    # Get bounding box from user boundary if it exists
    boundary_props = get_boundary_fc_props_for_user(request.user)

    map_view = MapView(
        height='100%',
        width='100%',
        controls=[
            'ZoomSlider', 'Rotate', 'FullScreen',
            {'ZoomToExtent': {
                'projection': 'EPSG:4326',
                'extent': boundary_props.get('bbox', [-180, -90, 180, 90])  # Default to World
            }}
        ],
        basemap=[
            'CartoDB',
            {'CartoDB': {'style': 'dark'}},
            'OpenStreetMap',
            'ESRI'
        ],
        view=MVView(
            projection='EPSG:4326',
            center=boundary_props.get('centroid', [0, 0]),  # Default to World
            zoom=boundary_props.get('zoom', 3),  # Default to World
            maxZoom=18,
            minZoom=2
        ),
        draw=MVDraw(
            controls=['Pan', 'Modify', 'Delete', 'Move', 'Point', 'Polygon', 'Box'],
            initial='Pan',
            output_format='GeoJSON'
        )
    )

3. Navigate to `<http://localhost:8000/apps/earth-engine/viewer/>`_ and verify that the default extent now frames the United States. Pan and zoom away from the United States. Press the **Fit to Extent** button (the **E** button just below the zoom bar in the top-left-hand side of the map) and verify that it zooms to the extents of the United States.

.. note::

    If a user has not uploaded a boundary, the default zoom will now encompass the globe. You can test this by deleting the boundary asset in the Google Earth Engine code editor.

6. Test and Verify
==================

Browse to `<http://localhost:8000/apps/earth-engine/viewer/>`_ in a web browser and login if necessary. Verify the following:

1. Upload a new zip archive containing a shapefile of the boundary of a country of your choice, other than the United States.
2. Navigate to `<https://code.earthengine.google.com/>`_ and verify that a new ``uploadToTableAsset`` task is kicked off.
3. When the ``uploadToTableAsset`` task completes, verify that the **boundary** asset has been created.
4. Navigate back to `<http://localhost:8000/apps/earth-engine/viewer/>`_ and refresh the page. Verify that the map frames the country whose boundary you uploaded.
5. Load a dataset of your choice and verify that the imagery is clipped by the boundary you uploaded.

7. Solution
===========

This concludes this portion of the GEE Tutorial. You can view the solution on GitHub at `<https://github.com/tethysplatform/tethysapp-earth_engine/tree/clip-by-asset-solution>`_ or clone it as follows:

.. parsed-literal::

    git clone https://github.com/tethysplatform/tethysapp-earth_engine
    cd tethysapp-earth_engine
    git checkout -b clip-by-asset-solution clip-by-asset-solution-|version|