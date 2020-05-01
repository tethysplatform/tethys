*************
Clip by Asset
*************

**Last Updated:** May 2020

In this tutorial you will learn how to upload a shapefile as a Google Earth Engine asset and use it to clip the imagery.

* Google Earth Engine Assets

1. Stub out New Method for Uploading Shapefiles to GEE
======================================================

1. Create new ``upload_shapefile_to_gee`` function in :file:`gee/methods.py` with the following contents: (print)

2. Import the new ``upload_shapefile_to_gee`` function and call it in ``handle_shapefile_upload`` function in :file:`controllers.py` after validating the shapefile upload. Also modify the ``try-except`` block to handle any uncaught Google Earth Engine errors:

.. code-block:: python

    from .gee.methods import upload_shapefile_to_gee

.. code-block:: python
    :emphasize-lines: 48-49, 54-57

    def handle_shapefile_upload(request, user_workspace):
        """
        Uploads shapefile to Google Earth Engine as an Asset.

        Args:
            request (django.Request): the request object.
            user_workspace (tethys_sdk.workspaces.Workspace): the User workspace object.

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

                    # Setup workspace directory for storing shapefile
                    workspace_dir = prep_boundary_dir(user_workspace.path)

                    # Write the shapefile to the workspace directory
                    write_boundary_shapefile(shp_file, workspace_dir)

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

1. Update the ``upload_shapefile_to_gee`` function in :file:`gee/methods.py` to convert the uploaded shapefile to GeoJSON:

2. Navigate to `<http://localhost:8000/apps/earth-engine/viewer/>`_ and upload the :file:`USA_simplified.zip`. Verify that the GeoJSON is being printed to the terminal where Tethys is running.

3. Update the ``upload_shapefile_to_gee`` function in :file:`gee/methods.py` to convert create ``ee.Features`` and an ``ee.FeatureCollection`` from the GeoJSON:

4. Navigate to `<http://localhost:8000/apps/earth-engine/viewer/>`_ and upload the :file:`USA_simplified.zip`. Verify that the new ``ee.FeatureCollection`` is printed to the terminal where Tethys is running.

3. Export the New ee.FeatureCollection to an Asset
==================================================

1. Create a new ``get_asset_dir_for_user`` function in :file:`gee/methods.py` with the following contents:

2. Create a new ``get_user_boundary_path`` function in :file:`gee/methods.py` with the following contents:

3. Update the ``upload_shapefile_to_gee`` function in :file:`gee/methods.py` to call the new ``get_user_boundary_path`` function and then export the ``ee.FeatureCollection`` to an asset at that path: (no try/except)

4. Navigate to `<http://localhost:8000/apps/earth-engine/viewer/>`_ and upload the :file:`USA_simplified.zip`. Verify that the path returned from ``get_user_boundary_path`` is printed to the terminal where Tethys is running.

.. note::

    If you have already uploaded an asset, doing so again will fail because we haven't handled the case where the file already exists (see Step 3.7). Either manually delete the asset at `<https://code.earthengine.google.com/>`_ or skip to step 3.8 for the implementation that handles this issue.

5. Navigate to `<https://code.earthengine.google.com/>`_ and select the **Tasks** tab in the top-right pane of the code editor. Verify that a new ``uploadToTableAsset`` task is/was running.

6. Once the ``uploadToTableAsset`` task is complete, select the **Assets** tab in the top-left pane of the code editor and verify that there is a new asset named **boundary** at the path that was printed to the terminal in step 3.4.

.. note::

    If the new asset does not appear, try pressing the refresh button.

7. Navigate to `<http://localhost:8000/apps/earth-engine/viewer/>`_ and upload the :file:`USA_simplified.zip` again. This should cause an error, because Google Earth Engine won't let you overwrite a file that already exists when exporting an asset.

8. Update the ``upload_shapefile_to_gee`` function in :file:`gee/methods.py` to delete the asset before exporting to asset. This will fail if there is no asset there (the first time), so handle with a ``try-except``: (with try/except this time)

9. Navigate to `<http://localhost:8000/apps/earth-engine/viewer/>`_ and upload the :file:`USA_simplified.zip` again. Verify that no error is shown this time.

10. Quickly navigate to `<https://code.earthengine.google.com/>`_ after successfully uploading the shapefile. Verify that a new ``uploadToTableAsset`` task is running and that the previous asset has been removed. Once the ``uploadToTableAsset`` job completes, the asset should once again be shown in the assets tab.

4. Use Boundary Asset to Clip Images
====================================

1. Create a new ``get_boundary_fc_for_user`` function in :file:`gee/methods.py` with the following contents:

2. Modify the ``get_image_collection_asset`` function in :file:`gee/methods.py` to call the new ``get_boundary_fc_for_user`` function and clip the imagery if something is returned:

.. TODO::

    Decide how to update the old tutorial with patch for new ``image_to_map_id`` to work with new versions of gee

3. Modify the call of ``get_image_collection_asset`` in the ``get_image_collection`` controller in :file:`controllers.py` to pass the ``request`` as an additional argument:

4. Navigate to `<http://localhost:8000/apps/earth-engine/viewer/>`_ and load a dataset of your choice. Verify that the imagery has been clipped to the United States. You'll need to manually pan and zoom to the U.S. to see the imagery.

5. Use Boundary Asset for Map Extents
=====================================

1. Create a new ``get_boundary_fc_props_for_user`` function in :file:`gee/methods.py` with the following contents:

2. Modify the ``viewer`` controller in :file:`controllers.py` to call the ``get_boundary_fc_props_for_user`` function and use the return properties to set the default extents for the map:

3. Navigate to `<http://localhost:8000/apps/earth-engine/viewer/>`_ and verify that the default extent now frames the United States. Pan and zoom away from the United States. Press the **Fit to Extent** button (the **E** button just below the zoom bar in the top-left-hand side of the map) and verify that it zooms to the extents of the United States.

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

This concludes this portion of the GEE Tutorial. You can view the solution on GitHub at `<https://github.com/tethysplatform/tethysapp-earth_engine/tree/clip-by-asset-solution-3.0>`_ or clone it as follows:

.. parsed-literal::

    git clone https://github.com/tethysplatform/tethysapp-earth_engine.git
    cd tethysapp-earth_engine
    git checkout -b clip-by-asset-solution clip-by-asset-solution-|version|