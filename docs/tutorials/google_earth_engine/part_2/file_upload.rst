***********
File Upload
***********

**Last Updated:** July 2024

In this tutorial you will add a file upload form to the Viewer page to allow users to provide a clipping boundary for the imagery. This will include writing validation code to ensure that only shapefiles containing Polygons are uploaded. The file will be stored in the user's media directory after being uploaded. The following topics will be reviewed in this tutorial:

* File Uploads via HTML Forms
* Validating Form Data
* User Media (:ref:`tethys_paths_api`)
* `Bootstrap Modals <https://getbootstrap.com/docs/5.2/components/modal/>`_
* Manipulating Shapefiles in Python with `pyshp <https://pypi.org/project/pyshp/>`_
* Temp Files

.. figure:: ../../../images/tutorial/gee/file_upload.png
    :width: 800px
    :align: center

0. Start From Previous Solution (Optional)
==========================================

If you wish to use the previous solution as a starting point:

.. parsed-literal::

    git clone https://github.com/tethysplatform/tethysapp-earth_engine
    cd tethysapp-earth_engine
    git checkout -b about-page-solution about-page-solution-|version|

1. Add New Modal for File Upload Form
=====================================

Create a new `Bootstrap Modal <https://getbootstrap.com/docs/5.2/components/modal/>`_ with a button in the left navigation to open it.

1. Add a new button titled **Set Boundary** to the bottom of the ``viewer`` controller in :file:`controllers.py`:

.. code-block:: python
    :emphasize-lines: 1-9, 21

    # Boundary Upload Form
    set_boundary_button = Button(
        name='set_boundary',
        display_text='Set Boundary',
        style='outline-secondary',
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

    return App.render(request, 'viewer.html', context)

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
      <p class="help mt-2">Draw an area of interest or drop a point, the press "Plot AOI" to view a plot of the data.</p>
      {% gizmo plot_button %}
      <p class="help mt-2">Upload a shapefile of a boundary to use to clip datasets and set the default extent.</p>
      {% gizmo set_boundary_button %}
    {% endblock %}


3. Add a new modal for the Set Boundary feature in the ``after_app_content`` block of :file:`templates/earth_engine/viewer.html`:

.. code-block:: html+django

    <!-- Set Boundary Modal -->
    <div class="modal fade" id="set-boundary-modal" tabindex="-1" role="dialog" aria-labelledby="set-boundary-modal-label">
      <div class="modal-dialog" role="document">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="set-boundary-modal-label">Set Boundary</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
          </div>
        </div>
      </div>
    </div>
    <!-- End Set Boundary Modal -->

4. Add the Bootstrap modal ``data-bs-toggle`` and ``data-bs-target`` attributes to the Set Boundary button so that it opens the modal when pressed. Update the Set Boundary button definition near the bottom of the ``viewer`` controller in :file:`controllers.py` as follows:

.. code-block:: python
    :emphasize-lines: 8-9

    # Boundary Upload Form
    set_boundary_button = Button(
        name='set_boundary',
        display_text='Set Boundary',
        style='outline-secondary',
        attributes={
            'id': 'set_boundary',
            'data-bs-toggle': 'modal',
            'data-bs-target': '#set-boundary-modal',  # ID of the Set Boundary Modal
        }
    )

5. Navigate to `<http://localhost:8000/apps/earth-engine/viewer/>`_ and verify that Set Boundary button opens the Set Boundary modal.

2. Add File Upload Form to Set Boundary Modal
=============================================

Add an HTML ``form`` element with the attributes that are required to perform a file upload. These include using a ``method`` of ``post`` and setting the ``enctype`` to ``multipart/form-data``. The form will also need an ``input`` element of type ``file``.

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

.. note::

    The Cross Site Request Forgery (CSRF) token is used to verify that the call came from our client-side code and not from a site posing to be our site. As a security precaution, the server will reject any POST requests that do not include this token. For more information about CSRF see: `Cross Site Request Forgery protection <https://docs.djangoproject.com/en/2.2/ref/csrf/>`_.

3. Add a ``<div>`` with an ``<input>`` element of type ``file`` to the new ``<form>`` element in :file:`templates/earth_engine/viewer.html`:

.. code-block:: html+django
    :emphasize-lines: 6-9

    <div class="modal-body">
      <form class="horizontal-form" id="set-boundary-form" method="post" action="" enctype="multipart/form-data">
        <p>Create a zip archive containing a shapefile and supporting files (i.e.: .shp, .shx, .dbf). Then use the file browser button below to select it.</p>
        <!-- This is required for POST method -->
        {% csrf_token %}
        <div id="boundary-file-form-group" class="mb-3">
          <label class="form-label" for="boundary-file">Boundary Shapefile</label>
          <input type="file" name="boundary-file" id="boundary-file" class="form-control" accept=".zip">
        </div>
      </form>
    </div>

4. Add a Submit button to the ``modal-footer`` element of the Set Boundary modal in :file:`templates/earth_engine/viewer.html`:

.. code-block:: html+django
    :emphasize-lines: 3

    <div class="modal-footer">
      <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
      <input type="submit" class="btn btn-secondary" value="Set Boundary" name="set-boundary-submit" id="set-boundary-submit" form="set-boundary-form">
    </div>

5. Navigate to `<http://localhost:8000/apps/earth-engine/viewer/>`_ and press the **Set Boundary** button. Verify that the modal opens and it contains a form with a file chooser button.

3. Handle File Upload in Controller
===================================

The ``action`` attribute of the HTML ``form`` element dictates endpoint to which to send the request. It is often set to a relative URL with a separate controller to handle the form submission (e.g. ``/apps/my-app/handle-file-upload``. If the ``action`` element is emtpy, then the form submission is submitted to the current URL, which means the same controller will handle the form submission as rendered it. This is the case with the file upload form you setup in the previous step. In this step you will add logic to the ``viewer`` controller to handle the file upload form submission. As this logic will get a little long, you'll first create a helper function that the ``viewer`` controller can call to handle the form submission.

1. Create a new helper function called ``handle_shapefile_upload`` in :file:`helpers.py`:

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

2. Import the ``handle_shapefile_upload`` function in :file:`controllers.py`:

.. code-block:: python

    from .helpers import handle_shapefile_upload

3. Call ``handle_shapefile_upload`` function in ``viewer`` controller in :file:`controllers.py` if a file has been uploaded. Also pass any error returned by the ``handle_shapefile_upload`` function to the context so that it can be displayed to the user:

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

    return App.render(request, 'viewer.html', context)

3. Navigate to `<http://localhost:8000/apps/earth-engine/viewer/>`_. Press the **Set Boundary** button to open the Set Boundary form. Choose a file and press the **Set Boundary** button in the modal to upload it. Verify that the name of the file is printed to the console.

4. Write Uploaded File to Temporary Directory
=============================================

With the ``handle_shapefile_upload`` helper function wired to be called by the ``viewer`` controller whenever a file is uploaded, you can now focus on building out the logic. The uploaded file is accessible through the ``request.FILES`` object and is stored in memory. To validate the file, you will need to write it to disk. In this step you will write the in-memory file to the temp directory. The built-in ``tempfile`` module makes it easy to write files to the temp directory in a cross-platform safe manner.

1. Add the following imports and replace ``handle_shapefile_upload`` in :file:`helpers.py` with this updated version that writes the in-memory file to the temp directory:

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

.. note::

    The temporary directory (``temp_dir``) and it's contents will be deleted as soon as the ``with`` statement is exited. Any additional logic that manipulates the ``temp_dir`` or ``temp_zip`` will need to occur within the ``with tempfile.TemporaryDirectory() as temp_dir:`` block.


2. Navigate to `<http://localhost:8000/apps/earth-engine/viewer/>`_ and upload a file. Verify a path in the :file:`/tmp` directory is printed to the console.

.. note::

    The file will no longer be at that path printed to the console because it is a temporary file. It is deleted as soon as the ``with tempfile.TemporaryDirectory() as temp_dir`` statement finishes.

5. Validate File Uploaded is a Zip Archive
==========================================

Now that the file is written to disk, use the built-in ``zipfile`` module to verify that the file is a ZIP archive. This is most easily done by attempting to extract the file and then handling the exception if it is not a ZIP file. This is a convenient pattern for this implementation, because the next step will be to verify that the ZIP archive contains a shapefile which will require extracting.

1. Add the following imports and modify ``handle_shapefile_upload`` in :file:`helpers.py` as follows:

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

2. Notice that the docstring for the ``handle_shapefile_upload`` helper function indicates that the return value should be an error string if there are errors. The logic added in the previous step includes the first ``return`` statement for the function, which occurs when the given file is not a ZIP file. Modify the Set Boundary form to display the error messages returned by the ``handle_shapefile_upload`` function. Replace the ``<div>`` with id ``boundary-file-form-group`` with this updated version in :file:`templates/earth_engine/viewer.html`:

.. code-block:: html+django
    :emphasize-lines: 3-6

    <div id="boundary-file-form-group" class="mb-3">
      <label class="form-label" for="boundary-file">Boundary Shapefile</label>
      <input type="file" name="boundary-file" id="boundary-file" class="form-control{% if set_boundary_error %} is-invalid{% endif %}" accept=".zip">
      {% if set_boundary_error %}
      <p class="invalid-feedback">{{ set_boundary_error }}</p>
      {% endif %}
    </div>

3. The modal is not open by default when the page loads, which is normally the desired behaviour. However, when the page refreshes after a form submission that yields errors, the errors will be obscured from the user until they open the dialog again. Automatically open the Set Boundary modal if there is an error to display. Replace the **INITIALIZATION / CONSTRUCTOR** section of :file:`public/js/gee_datasets.js` with the following:

.. code-block:: javascript
    :emphasize-lines: 21-26

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
        if ($('#boundary-file').hasClass('is-invalid')) {
            let boundary_modal_elem = document.getElementById('set-boundary-modal');
            let boundary_modal_inst = bootstrap.Modal.getOrCreateInstance(boundary_modal_elem);
            boundary_modal_inst.show();
        }
    });

4. Navigate to `<http://localhost:8000/apps/earth-engine/viewer/>`_ and upload a non-zip file. Verify that the error message is displayed in the modal and that it opens automatically. Upload a zip file and verify that the modal does not open automatically and no error is displayed when you open it.

6. Validate File is a Shapefile Containing Polygons
===================================================

In this step you will add the logic to validate that the file contained in the ZIP archive is a shapefile. You will use the ``pyshp`` library to do this, which will introduce a new dependency for the app.

1. Install ``pyshp`` library into your Tethys conda environment using conda or pip. Run the following command in the terminal with your Tethys environment activated:

.. code-block:: bash

    # conda: conda-forge channel highly recommended
    conda install -c conda-forge pyshp

    # pip
    pip install pyshp

2. Add ``pyshp`` as a new dependency in the ``install.yml``:

.. code-block:: yaml
    :emphasize-lines: 20

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
      pip:

    post:

3. Add the following imports and create a new helper function ``find_shapefile`` in :file:`helpers.py`:

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


4. Use the new ``find_shapefile`` helper function and ``pyshp`` in ``handle_shapefile_upload`` to validate that the unzipped directory contains a shapefile. Update ``handle_shapefile_upload`` in :file:`helpers.py`:

.. code-block:: python

    import shapefile

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

7. Save Shapefile to the User's Media Directory
===================================================

At this point you have confirmed that the user uploaded a ZIP archive containing a shapefile of polygons but the file is still stored as a temporary file and will be deleted as soon as the code finishes executing. In this step you will add the logic to write the file to the user's media directory. This will involve creating a few new helper functions and using the :ref:`tethys_paths_api`.

1. The shapefile and its sidecars will be stored in a directory called :file:`boundary` within the user's media directory. Only one boundary shapefile will be stored for each user, so if the :file:`boundary` directory already exists, it will need to be cleared out. The ``prep_boundary_dir`` helper function will be responsible for initializing the :file:`boundary` directory in the user's media directory and clearing it out if needed. Add the following imports and create the ``prep_boundary_dir`` function in :file:`helpers.py`:

.. code-block:: python

    import glob

.. code-block:: python

    def prep_boundary_dir(root_path):
        """
        Setup the media directory that will store the uploaded boundary shapefile.

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

2. The ``write_boundary_shapefile`` helper function takes the ``shapefile.Reader`` object that was used to validate the shapefile and uses it to write a copy of the shapefile to the given directory. Create the ``write_boundary_shapefile`` function in :file:`helpers.py`:

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

3. The ``controller`` decorator provides arguments for adding the user and app media directories. Add the ``user_media`` argument and set it to ``True`` in the ``controller`` decorator for the ``viewer`` function. The decorator passes the user media object as an additional argument to the controller, so you will need to add an additional argument to accept the user media in :file:`controllers.py`:

.. code-block:: python
    :emphasize-lines: 1-2

    @controller(user_media=True, url='viewer')
    def viewer(request, user_media):
        """
        Controller for the app viewer page.
        """


.. tip::

    For more information about User Media, see :ref:`tethys_paths_api`.

4. The ``viewer`` controller will need to be able to pass the ``user_media`` to the ``handle_shapefile_upload`` function. Modify the ``handle_shapefile_upload`` helper function to accept the ``user_media`` as an additional argument in :file:`helpers.py`:

.. code-block:: python
    :emphasize-lines: 1

    def handle_shapefile_upload(request, user_media):
        """
        Uploads shapefile to Google Earth Engine as an Asset.

        Args:
            request (django.Request): the request object.
            user_media (tethys_sdk.paths.TethysPath): the User media object.

        Returns:
            str: Error string if errors occurred.
        """

5. Add logic to write the uploaded shapefile to the user media directory in ``handle_shapefile_upload`` in :file:`helpers.py`:

.. code-block:: python
    :emphasize-lines: 45-49

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

            except TypeError:
                return 'Incomplete or corrupted shapefile provided.'

6. Modify the ``handle_shapefile_upload`` call in the ``viewer`` controller in :file:`controllers.py` to pass the user media path:

.. code-block:: python
    :emphasize-lines: 4

    # Handle Set Boundary Form
    set_boundary_error = ''
    if request.POST and request.FILES:
        set_boundary_error = handle_shapefile_upload(request, user_media)

7. Navigate to `<http://localhost:8000/apps/earth-engine/viewer/>`_ and upload the :file:`USA_simplified.zip`. Verify that the shapefile is saved to the active user's media directory with its sidecar files 
(e.g. :file:`~/.tethys/tethys/media/earth_engine/user/admin/boundary/boundary.shp`).

.. note::

    The exact path to the user media directory will vary based on your Tethys installation and the active user. To find the path to the user media directory you can use this command:

    .. code-block:: bash

        tethys paths get -t user_media --user <username> --app earth_engine
    

8. Redirect Upon Successful File Upload
=======================================

As a final user experience improvement, issue a redirect response instead of the normal response when there are now errors. This will clear the form and reset the state of the page.

1. Add the logic to the ``viewer`` controller in :file:`controllers.py`:

.. code-block:: python

    from django.http import HttpResponseRedirect

.. code-block:: python
    :emphasize-lines: 6-8

    # Handle Set Boundary Form
    set_boundary_error = ''
    if request.POST and request.FILES:
        set_boundary_error = handle_shapefile_upload(request, user_media)

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
6. Verify that the :file:`boundary.shp` is written to the user media directory of the active user (e.g. :file:`~/.tethys/tethys/media/earth_engine/user/admin/boundary/boundary.shp`).
7. Press the *Home* button in the header to navigate to the home page. Verify that no warnings are displayed after a successful upload when navigating away.

10. Solution
============

This concludes this portion of the GEE Tutorial. You can view the solution on GitHub at `<https://github.com/tethysplatform/tethysapp-earth_engine/tree/file-upload-solution>`_ or clone it as follows:

.. parsed-literal::

    git clone https://github.com/tethysplatform/tethysapp-earth_engine
    cd tethysapp-earth_engine
    git checkout -b file-upload-solution file-upload-solution-|version|
