***********
File Upload
***********

**Last Updated:** May 2020

In this tutorial you will learn how to upload files using HTML forms. Topics covered in this tutorial include:

* File Uploads via HTML Forms
* Validating Form Data
* User Workspaces
* pyshp

1. Add a Set Button and Modal for Shapefile Upload
==================================================

1. Add a new Set boundary button to the bottom of the ``viewer`` controller in :file:`controllers.py`:

.. code-block:: python
    :emphasize-lines: 1-9, 21

    # Boundary Upload Form
    set_boundary_button = Button(
        name='set_boundary',
        display_text='Set Boundary',
        style='default',
        attributes={
            'id': 'set_boundary',
        }
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
        'plot_button': plot_button,
        'set_boundary_button': set_boundary_button,
        'ee_products': EE_PRODUCTS,
        'map_view': map_view
    }

    return render(request, 'earth_engine/viewer.html', context)

2. Add the new button with help text to the ``app_navigation_items`` block in :file:`templates/earth_engine/viewer.html`:

.. code-block:: html+django
    :emphasize-lines: 14-15

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
      <p class="help">Draw an area of interest or drop a point, the press "Plot AOI" to view a plot of the data.</p>
      {% gizmo plot_button %}
      <p class="help">Upload a shapefile of a boundary to use to clip datasets and set the default extent.</p>
      {% gizmo set_boundary_button %}
    {% endblock %}


3. Add a new modal for the Set Boundary feature in the ``after_app_content`` block of :file:`templates/earth_engine/viewer.html`:

.. code-block:: html+django

    <!-- Set Boundary Modal -->
    <div class="modal fade" id="set-boundary-modal" tabindex="-1" role="dialog" aria-labelledby="set-boundary-modal-label">
      <div class="modal-dialog" role="document">
        <div class="modal-content">
          <div class="modal-header">
            <button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button>
            <h5 class="modal-title" id="set-boundary-modal-label">Set Boundary</h5>
          </div>
          <div class="modal-body">
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-default" data-dismiss="modal">Cancel</button>
          </div>
        </div>
      </div>
    </div>
    <!-- End Set Boundary Modal -->

4. Add the Bootstrap modal ``data-toggle`` and ``data-target`` attributes to the Set Boundary button so that it opens the modal when pressed:

.. code-block:: python
    :emphasize-lines: 8-9

    # Boundary Upload Form
    set_boundary_button = Button(
        name='set_boundary',
        display_text='Set Boundary',
        style='default',
        attributes={
            'id': 'set_boundary',
            'data-toggle': 'modal',
            'data-target': '#set-boundary-modal'  # ID of the Set Boundary Modal
        }
    )

5. Navigate to `<http://localhost:8000/apps/earth-engine/viewer/>`_ and verify that Set Boundary button opens the Set Boundary Modal.

2. Add File Upload Form to Set Boundary Modal
=============================================

1. Add a ``<form>`` element to the ``modal-body`` element of the Set Boundary modal in :file:`templates/earth_engine/viewer.html`:

..  code-block:: html+django
    :emphasize-lines: 2-4

    <div class="modal-body">
      <form class="horizontal-form" id="set-boundary-form" method="post" action="" enctype="multipart/form-data">
        <p>Create a zip archive containing a shapefile and supporting files (i.e.: .shp, .shx, .dbf). Then use the file browser button below to select it.</p>
      </form>
    </div>

2. Add the Cross Site Request Forgery token (``csrf_token``) to the new ``<form>`` element in :file:`templates/earth_engine/viewer.html`:

.. code-block:: html+django
    :emphasize-lines: 4-5

    <div class="modal-body">
      <form class="horizontal-form" id="set-boundary-form" method="post" action="" enctype="multipart/form-data">
        <p>Create a zip archive containing a shapefile and supporting files (i.e.: .shp, .shx, .dbf). Then use the file browser button below to select it.</p>
        <!-- This is required for POST method -->
        {% csrf_token %}
      </form>
    </div>

3. Add a Bootstrap ``form-group`` with an ``<input>`` element of type ``file`` to the new ``<form>`` element in :file:`templates/earth_engine/viewer.html`:

.. code-block:: html+django
    :emphasize-lines: 6-9

    <div class="modal-body">
      <form class="horizontal-form" id="set-boundary-form" method="post" action="" enctype="multipart/form-data">
        <p>Create a zip archive containing a shapefile and supporting files (i.e.: .shp, .shx, .dbf). Then use the file browser button below to select it.</p>
        <!-- This is required for POST method -->
        {% csrf_token %}
        <div id="boundary-file-form-group" class="form-group">
          <label class="control-label" for="boundary-file">Boundary Shapefile</label>
          <input type="file" name="boundary-file" id="boundary-file" accept="zip">
        </div>
      </form>
    </div>

4. Add a Submit button to the ``modal-footer`` element of the Set Boundary modal in :file:`templates/earth_engine/viewer.html`:

.. code-block:: html+django
    :emphasize-lines: 3

    <div class="modal-footer">
      <button type="button" class="btn btn-default" data-dismiss="modal">Cancel</button>
      <input type="submit" class="btn btn-default" value="Set Boundary" name="set-boundary-submit" id="set-boundary-submit" form="set-boundary-form">
    </div>

3. Handle File Upload in Controller
===================================

1. Create a new helper function called ``handle_shapefile_upload`` in :file:`controllers.py`:

.. code-block:: python

    def handle_shapefile_upload(request):
        """
        Uploads shapefile to Google Earth Engine as an Asset.

        Args:
            request (django.Request): the request object.

        Returns:
            str: Error string if errors occurred.
        """
        # Write file to temp for processing
        uploaded_file = request.FILES['boundary-file']
        print(uploaded_file)

2. Call ``handle_shapefile_upload`` function in ``viewer`` controller in :file:`controllers.py` if a file has been uploaded and pass any error returned to the context for later use in the template:

.. code-block:: python
    :emphasize-lines: 1-4, 17

    # Handle Set Boundary Form
    set_boundary_error = ''
    if request.POST and request.FILES:
        set_boundary_error = handle_shapefile_upload(request)

    context = {
        'platform_select': platform_select,
        'sensor_select': sensor_select,
        'product_select': product_select,
        'start_date': start_date,
        'end_date': end_date,
        'reducer_select': reducer_select,
        'load_button': load_button,
        'clear_button': clear_button,
        'plot_button': plot_button,
        'set_boundary_button': set_boundary_button,
        'set_boundary_error': set_boundary_error,
        'ee_products': EE_PRODUCTS,
        'map_view': map_view
    }

    return render(request, 'earth_engine/viewer.html', context)

3. Navigate to `<http://localhost:8000/apps/earth-engine/viewer/>`_ and upload a file. Verify that information about the uploaded file is printed to the console.

4. Write Uploaded File to Temporary Directory
=============================================

1. Add the following imports and replace ``handle_shapefile_upload`` in :file:`controllers.py` with this updated version:

.. code-block:: python

    import os
    import tempfile

.. code-block:: python
    :emphasize-lines: 14-21

    def handle_shapefile_upload(request):
        """
        Uploads shapefile to Google Earth Engine as an Asset.

        Args:
            request (django.Request): the request object.

        Returns:
            str: Error string if errors occurred.
        """
        # Write file to temp for processing
        uploaded_file = request.FILES['boundary-file']

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_zip_path = os.path.join(temp_dir, 'boundary.zip')
            print(temp_zip_path)

            # Use with statements to ensure opened files are closed when done
            with open(temp_zip_path, 'wb') as temp_zip:
                for chunk in uploaded_file.chunks():
                    temp_zip.write(chunk)


2. Navigate to `<http://localhost:8000/apps/earth-engine/viewer/>`_ and upload a file. Verify that the file is written to the temporary location printed to the console.

5. Validate File Uploaded is a Zip Archive
==========================================

1. Add the following imports and modify ``handle_shapefile_upload`` in :file:`controllers.py` as follows:

.. code-block:: python

    import zipfile

.. code-block:: python
    :emphasize-lines: 22-29

    def handle_shapefile_upload(request):
        """
        Uploads shapefile to Google Earth Engine as an Asset.

        Args:
            request (django.Request): the request object.

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

.. note::

    Any string returned by this function will be displayed as an error message to the user.

2. Modify the Set Boundary Form to display the error message. Replace the ``<div>`` with id ``boundary-file-form-group`` with this updated version in :file:`templates/earth_engine/viewer.html`:

.. code-block:: html+django
    :emphasize-lines: 1, 4-6

    <div id="boundary-file-form-group" class="form-group{% if set_boundary_error %} has-error{% endif %}">
      <label class="control-label" for="boundary-file">Boundary Shapefile</label>
      <input type="file" name="boundary-file" id="boundary-file" accept="zip">
      {% if set_boundary_error %}
      <p class="help-block">{{ set_boundary_error }}</p>
      {% endif %}
    </div>

3. Automatically open the Set Boundary modal if there is an error to display. Replace the **INITIALIZATION / CONSTRUCTOR** section of :file:`public/js/gee_datasets.js` with the following:

.. code-block:: javascript
    :emphasize-lines: 21-24

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

        // Open boundary file modal if it has an error
        if ($('#boundary-file-form-group').hasClass('has-error')) {
            $('#set-boundary-modal').modal('show');
        }
    });

4. Navigate to `<http://localhost:8000/apps/earth-engine/viewer/>`_ and upload a non-zip file. Verify that the error message is displayed in the modal and that it opens automatically. Upload a zip file and verify that the modal does not open automatically and no error is displayed.

6. Validate File is a Shapefile Containing Polygons
===================================================

1. Install ``pyshp`` library for working with shapefiles. Run the following command in the terminal with your Tethys environment activated:

.. code-block:: bash

    conda install -c conda-forge pyshp

2. Add ``pyshp`` as a new dependency in the ``install.yaml``:

.. code-block:: yaml
    :emphasize-lines: 16

    # This file should be committed to your app code.
    version: 1.0
    # This should match the app - package name in your setup.py
    name: earth_engine

    requirements:
      # Putting in a skip true param will skip the entire section. Ignoring the option will assume it be set to False
      skip: false
      conda:
        channels:
          - conda-forge
        packages:
          - earthengine-api=0.1.205
          - oauth2client
          - geojson
          - pyshp
      pip:

    post:

3. Add the following imports and create a new helper function ``find_shapefile`` in :file:`helpers.py`:

.. code-block:: python

    import shapefile

.. code-block:: python

    def find_shapefile(directory):
        """
        Recursively find the path to the first file with an extension ".shp" in the given directory.

        Args:
            directory (str): Path of directory to search for shapefile.

        Returns:
            str: Path to first shapefile found in given directory.
        """
        shapefile_path = ''

        # Scan the temp directory using walk, searching for a shapefile (.shp extension)
        for root, dirs, files in os.walk(directory):
            for f in files:
                f_path = os.path.join(root, f)
                f_ext = os.path.splitext(f_path)[1]

                if f_ext == '.shp':
                    shapefile_path = f_path
                    break

        return shapefile_path


4. Add logic to validate that the unzipped directory contains a shapefile and that it only contains polygons in ``handle_shapefile_upload`` in :file:`controllers.py`:

.. code-block:: python

    import shapefile
    from tethysapp.earth_engine.helpers import generate_figure, compute_dates_for_product, find_shapefile

.. code-block:: python
    :emphasize-lines: 31-45

    def handle_shapefile_upload(request):
        """
        Uploads shapefile to Google Earth Engine as an Asset.

        Args:
            request (django.Request): the request object.

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

            except TypeError:
                return 'Incomplete or corrupted shapefile provided.'

5. Download :download:`USA_simplified.zip <./resources/USA_simplified.zip>`, a zip archive containing a simplified shapefile of the boundary of the United States. Also download :download:`points.zip <./resources/points.zip>`, an archive containing a shapefile with only points.

6. Navigate to `<http://localhost:8000/apps/earth-engine/viewer/>`_ and verify the following:

    * Upload the :file:`USA_simplified.zip` and verify that no errors are shown.
    * Upload the :file:`points.zip` and verify that an error *is* shown.
    * Create a zip archive that does not contain a shapefile and upload it. Verify an error *is* shown.

7. Write Shapefile to the User's Workspace Directory
====================================================

1. Add the following imports and create a new helper function ``prep_boundary_dir`` in :file:`helpers.py`:

.. code-block:: python

    import glob

.. code-block:: python

    def prep_boundary_dir(root_path):
        """
        Setup the workspace directory that will store the uploaded boundary shapefile.

        Args:
            root_path (str): path to the root directory where the boundary directory will be located.

        Returns:
            str: path to boundary directory for storing boundary shapefile.
        """
        # Copy into new shapefile in user directory
        boundary_dir = os.path.join(root_path, 'boundary')

        # Make the directory if it doesn't exist
        if not os.path.isdir(boundary_dir):
            os.mkdir(boundary_dir)

        # Clear the directory if it exists
        else:
            # Find all files in the directory using glob
            files = glob.glob(os.path.join(boundary_dir, '*'))

            # Remove all the files
            for f in files:
                os.remove(f)

        return boundary_dir

2. Create a new helper function ``write_boundary_shapefile`` in :file:`helpers.py`:

.. code-block:: python

    def write_boundary_shapefile(shp_file, directory):
        """
        Write the shapefile to the given directory. The shapefile will be called "boundary.shp".

        Args:
            shp_file (shapefile.Reader): A shapefile reader object.
            directory (str): Path to directory to which to write shapefile.

        Returns:
            str: path to shapefile that was written.
        """
        # Name the shapefiles boundary.* (boundary.shp, boundary.dbf, boundary.shx)
        shapefile_path = os.path.join(directory, 'boundary')

        # Write contents of shapefile to new shapfile
        with shapefile.Writer(shapefile_path) as out_shp:
            # Based on https://pypi.org/project/pyshp/#examples
            out_shp.fields = shp_file.fields[1:]  # skip the deletion field

            # Add the existing shape objects
            for shaperec in shp_file.iterShapeRecords():
                out_shp.record(*shaperec.record)
                out_shp.shape(shaperec.shape)

        return shapefile_path

3. Add the ``user_workspace`` decorator to the ``viewer`` controller. The user workspace will be passed in as an additional argument to the controller, so don't forget to add an additional argument to accept the user workspace in :file:`controllers.py`:

.. code-block:: python

    from tethys_sdk.workspaces import user_workspace

.. code-block:: python
    :emphasize-lines: 2-3

    @login_required()
    @user_workspace
    def viewer(request, user_workspace):
        """
        Controller for the app home page.
        """

4. Modify the ``handle_shapefile_upload`` helper function to accept the ``user_workspace`` as an additional argument in :file:`controllers.py`:

.. code-block:: python
    :emphasize-lines: 1

    def handle_shapefile_upload(request, user_workspace):
        """
        Uploads shapefile to Google Earth Engine as an Asset.

        Args:
            request (django.Request): the request object.
            user_workspace (tethys_sdk.workspaces.Workspace): the User workspace object.

        Returns:
            str: Error string if errors occurred.
        """

5. Add logic to write the uploaded shapefile to the user workspace in ``handle_shapefile_upload`` in :file:`controllers.py`:

.. code-block:: python
    :emphasize-lines: 45-49

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

            except TypeError:
                return 'Incomplete or corrupted shapefile provided.'

6. Modify the ``handle_shapefile_upload`` call in the ``viewer`` controller in :file:`controllers.py` to pass the user workspace path:

.. code-block:: python
    :emphasize-lines: 4

    # Handle Set Boundary Form
    set_boundary_error = ''
    if request.POST and request.FILES:
        set_boundary_error = handle_shapefile_upload(request, user_workspace)

7. Navigate to `<http://localhost:8000/apps/earth-engine/viewer/>`_ and upload the :file:`USA_simplified.zip`. Verify that the shapefile is saved to the active user's workspace directory with its sidecar files (e.g. :file:`workspaces/user_workspaces/admin/boundary.shp`).

8. Redirect Upon Successful File Upload
=======================================

1. If there are no errors returned by ``handle_shapefile_upload``, redirect back to same page to clear the form data. Add the logic to the ``viewer`` controller in :file:`controllers.py`:

.. code-block:: python
    :emphasize-lines: 6-8

    # Handle Set Boundary Form
    set_boundary_error = ''
    if request.POST and request.FILES:
        set_boundary_error = handle_shapefile_upload(request, user_workspace)

        if not set_boundary_error:
            # Redirect back to this page to clear form
            return HttpResponseRedirect(request.path)

2. Navigate to `<http://localhost:8000/apps/earth-engine/viewer/>`_ and upload the :file:`USA_simplified.zip`. Navigate to a different page of the app and verify that no warning messages are displayed indicating that changes to the form may be lost.

9. Test and Verify
==================

Browse to `<http://localhost:8000/apps/earth-engine/viewer/>`_ in a web browser and login if necessary. Verify the following:

1. Verify that Set Boundary button opens the Set Boundary Modal.
2. Upload a non-zip file and verify that the appropriate error is displayed.
3. Upload a zip archive that does not contain a shapefile and verify that the appropriate error is displayed.
4. Upload the :file:`points.zip` and verify that the appropriate error is displayed.
5. Upload the :file:`USA_simplified.zip` and verify that **no** errors are displayed.
6. Verify that the :file:`boundary.shp` is written to the user workspace of the active user (e.g. :file:`workspaces/user_workspace/admin/boundary/boundary.shp`).
7. Press the *Home* button in the header to navigate to the home page. Verify that no warnings are displayed after a successful upload when navigating away.

10. Solution
============

This concludes this portion of the GEE Tutorial. You can view the solution on GitHub at `<https://github.com/tethysplatform/tethysapp-earth_engine/tree/file-upload-solution-3.0>`_ or clone it as follows:

.. parsed-literal::

    git clone https://github.com/tethysplatform/tethysapp-earth_engine.git
    cd tethysapp-earth_engine
    git checkout -b file-upload-solution file-upload-solution-|version|
