.. _upload_shape_file_to_geoserver_recipe :

**********************************
Uploading Shapefiles to GeoServer
**********************************

**Last Updated:** October 2025

Start with the :ref:`Spatial Dataset Service Recipe <spatial_dataset_service_recipe>`

This recipe will show you how to upload shapefiles to your GeoServer Spatial Dataset Service. These shapefiles can later be displayed on maps. You can learn how in the :ref:`MapLayout WMS Layer Recipe <wms_layer_map_layout_recipe>` or :ref:`MapView WMS Layer Recipe <wms_layer_map_view_recipe>`

Add Upload Form to Page
#######################

Begin by adding the following contents in your app's template.

.. code-block:: html+django

    <h1>Upload a shapefile</h1>
    <form action="" method="post" enctype="multipart/form-data">
        {% csrf_token %}
        <div class="mb-3">
            <label for="fileInput" class="form-label">Shapefiles</label>
            <input name="files" type="file" multiple class="form-control" id="fileInput" placeholder="Shapefiles">
        </div>
        <input name="submit" type="submit" class="btn btn-secondary">
    </form>

Handle File Upload in Controller
################################

For this recipe, we'll use the same controller to handle your file upload, as the one that renders the template you've added your upload form to. 

Add the following to your controller:

You can change these variables according to your app's name.

.. code-block:: python

    WORKSPACE = 'geoserver_app'
    GEOSERVER_URI = 'http://www.example.com/geoserver-app'

    @controller
    def home(request):
        """
        Controller for the app home page.
        """
        # Retrieve a geoserver engine
        geoserver_engine = App.get_spatial_dataset_service(name='main_geoserver', as_engine=True)

        # Check for workspace and create workspace for app if it doesn't exist
        response = geoserver_engine.list_workspaces()

        if response['success']:
            workspaces = response['result']

            if WORKSPACE not in workspaces:
                from urllib.parse import urlparse
                parsed = urlparse(geoserver_engine.public_endpoint)
                uri = f'{parsed.scheme}://{parsed.netloc}/{WORKSPACE}'
                geoserver_engine.create_workspace(workspace_id=WORKSPACE, uri=uri)

        # Case where the form has been submitted
        if request.POST and 'submit' in request.POST:
            # Verify files are included with the form
            if request.FILES and 'files' in request.FILES:
                # Get a list of the files
                file_list = request.FILES.getlist('files')

                # Upload shapefile
                store = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(6))
                store_id = WORKSPACE + ':' + store
                geoserver_engine.create_shapefile_resource(
                    store_id=store_id,
                    shapefile_upload=file_list,
                    overwrite=True
                )

        context = {}

        return App.render(request, 'home.html', context)

        
Download Test Files
###################

Download the sample shapefiles that you will upload to GeoServer:

:download:`geoserver_app_data.zip <../../tutorials/geoserver/geoserver_app_data.zip>`

The archive contains several shapefiles organized into folders. Unzip the archive to your preferred location and inspect the files.

Upload Shapefile
################

Go to the page in your app with your new form and you should see a new file input ("Browse" button or something similar) and your submit button. Click the "Browse" button and upload one of the shapefiles from the files you downloaded. Remember, for the shapefile to be valid you need to select at least the files with the extensions: "shp", "shx", and "dbf". Press submit to upload those files.

Now use the GeoServer web admin interface (`<http://localhost:8181/geoserver/web/>`_) to verify that the layers were successfully uploaded. Look for layers belonging to the workspace name you assigned in your  `WORKSPACE` variable earlier.

From here, you can display that shapefile on an interactive map using either the :ref:`Map Layout WMS Layer Recipe <wms_layer_map_layout_recipe>` or the :ref:`Map View WMS Layer Recipe <wms_layer_map_view_recipe>`

