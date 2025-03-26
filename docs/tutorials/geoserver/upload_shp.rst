****************
Upload Shapefile
****************

**Last Updated:** July 2024

1. Add Form to Home Page
========================

Replace the contents of the existing :file:`home.html` template with:

.. code-block:: html+django

    {% extends "geoserver_app/base.html" %}

    {% block app_content %}
      <h1>Upload a Shapefile</h1>
      <form action="" method="post" enctype="multipart/form-data">.
        {% csrf_token %}
        <div class="mb-3">
            <label for="fileInput" class="form-label">Shapefiles</label>
            <input name="files" type="file" multiple class="form-control" id="fileInput" placeholder="Shapefiles">
        </div>
        <input name="submit" type="submit" class="btn btn-secondary">
      </form>
    {% endblock %}

2. Handle File Upload in Home Controller
========================================

Replace the contents of :file:`controllers.py` module with the following:

.. code-block:: python

    import random
    import string

    from tethys_sdk.routing import controller

    from tethys_sdk.gizmos import *
    from .app import App


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


3. Test Shapefile Upload
========================

Go to the home page of your app located at `<http://localhost:8000/apps/geoserver-app/>`_. You should see a form with a file input ("Browse" button or similar) and a submit button. To test this page, select the "Browse" button and upload one of the shapefiles from the data that you downloaded earlier. Remember that for the shapefile to be valid, you need to select at least the files with the extensions "shp", "shx", and "dbf". Press submit to upload the files.

Use the GeoServer web admin interface (`<http://localhost:8181/geoserver/web/>`_) to verify that the layers were successfully uploaded. Look for layers belonging to the workspace 'geoserver_app'.

4. Solution
===========

This concludes the this part of the GeoServer tutorial. You can view the solution on GitHub at `<https://github.com/tethysplatform/tethysapp-geoserver_app>`_ or clone it as follows:

.. parsed-literal::

    git clone https://github.com/tethysplatform/tethysapp-geoserver_app
    cd tethysapp-geoserver_app
    git checkout -b upload-shapefile-solution upload-shapefile-solution-|version|