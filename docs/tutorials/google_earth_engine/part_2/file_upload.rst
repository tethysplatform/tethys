***********
File Upload
***********

**Last Updated:** May 2019

1. Add a Set Button and Modal for Shapefile Upload
==================================================

1. Add a new Set boundary button the ``viewer`` controller in :file:`controllers.py`:

2. Add the new button with help text to the ``app_navigation_items`` block in :file:`templates/earth_engine/viewer.html`:

3. Add a new modal for the Set Boundary feature in the ``after_app_content`` block of :file:`templates/earth_engine/viewer.html`:

4. Add the ``data-toggle`` and ``data-target`` attributes to the Set Boundary button so that it opens the modal:

5. Navigate to `<http://localhost:8000/apps/earth-engine/viewer/>`_ and verify that Set Boundary button opens the Set Boundary Modal.

2. Add File Upload Form to Set Boundary Modal
=============================================

1. Add a ``<form>`` element to the ``modal-body`` element of the Set Boundary modal in :file:`templates/earth_engine/viewer.html`:

2. Add a Bootstrap ``form-group`` with an ``<input>`` element of type ``file`` to the new ``<form>`` element in :file:`templates/earth_engine/viewer.html`: (NO ERROR)

3. Add a Submit button to the ``modal-footer`` element of the Set Boundary modal in :file:`templates/earth_engine/viewer.html`:

3. Handle File Upload in Controller
===================================

1. Create a new helper function called ``handle_shapefile_upload`` in :file:`helpers.py`:

2. Call ``handle_shapefile_upload`` function in ``viewer`` controller in :file:`helpers.py` if a file has been uploaded:

3. Navigate to `<http://localhost:8000/apps/earth-engine/viewer/>`_ and upload a file. Verify that the path the file is printed to the terminal when a file is uploaded.

4. Write Uploaded File to Temporary Directory
=============================================

1. Modify ``handle_shapefile_upload`` in :file:`helpers.py` as follows: (59-71, with print path to temp file)

2. Navigate to `<http://localhost:8000/apps/earth-engine/viewer/>`_ and upload a file. Verify that the file is written to the location printed to the console.

5. Validate File Uploaded is a Zip Archive
==========================================

1. Modify ``handle_shapefile_upload`` in :file:`helpers.py` as follows: (73-80)

2. Pass the error returned by ``handle_shapefile_upload``, if any, to the template in the ``viewer`` controller of :file:`controllers.py`:

3. Modify the Set Boundary Form to display the error message in :file:`templates/earth_engine/viewer.html`:

4. Add the following to :file:`public/js/gee_datasets.js` to automatically open the Set Boundary model if there is an error:

5. Navigate to `<http://localhost:8000/apps/earth-engine/viewer/>`_ and upload a non-zip file. Verify that the error message is displayed in the modal and it opens automatically. Upload a zip file and verify that the modal does not open automatically and no error is displayed.

6. Validate File is a Shapefile Containing Polygons
===================================================

1. Install ``pyshp`` library for working with shapefiles:

2. Add ``pyshp`` as a new dependency in ``install.yaml``:

3. Create a new helper function ``find_shapefile`` in :file:`helpers.py`:

4. Add logic to validate that the unzipped directory contains a shapefile and that it only contains polygons in ``handle_shapefile_upload`` in :file:`helpers.py`:

5. Download <download link>, a zip archive containing a shapefile of the boundary of <some country>. Also download <download link>, an archive containing a shapefile with only points.

6. Navigate to `<http://localhost:8000/apps/earth-engine/viewer/>`_ and upload the <country zip>. Verify that no errors are returned. Upload the <points zip> and verify that an error is shown.

7. Create a zip archive that does not contain a shapefile and upload it. Verify an error is shown.

7. Write Shapefile to the User's Workspace Directory
====================================================

1. Create a new helper function ``prep_boundary_dir`` in :file:`helpers.py`:

2. Create a new helper function ``write_boundary_shapefile`` in :file:`helpers.py`:

3. Add the ``user_workspace`` decorator to the ``viewer`` controller, adding an additional argument to accept the user workspace in :file:`controllers.py`:

4. Modify the ``handle_shapefile_upload`` helper function to accept the ``user_workspace`` as an additional argument in :file:`helpers.py`:

5. Add logic to write the uploaded shapefile to the user workspace in ``handle_shapefile_upload`` in :file:`helpers.py`:

6. Modify the ``handle_shapefile_upload`` call in the ``viewer`` controller to pass the user workspace path in :file:`controllers.py`:

7. Navigate to `<http://localhost:8000/apps/earth-engine/viewer/>`_ and upload the <country zip>. Verify that the shapefile is saved to the active user's workspace directory with its sidecar files (e.g. :file:`workspaces/user_workspaces/admin/boundary.shp`).

8. Solution
===========

This concludes this portion of the GEE Tutorial. You can view the solution on GitHub at `<https://github.com/tethysplatform/tethysapp-earth_engine/tree/file-upload-solution-3.0>`_ or clone it as follows:

.. parsed-literal::

    git clone https://github.com/tethysplatform/tethysapp-earth_engine.git
    cd tethysapp-earth_engine
    git checkout -b file-upload-solution file-upload-solution-|version|
