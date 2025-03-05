*********
Data Prep
*********

**Last Updated:** July 2024

In this tutorial you will get you familiar with sample NextGen data and prepare it for use in your Tethys application.

0. Start From Previous Solution (Optional)
==========================================

If you wish to use the previous solution as a starting point:

.. parsed-literal::

    git clone https://github.com/tethysplatform/tethysapp-map_layout_tutorial
    cd tethysapp-map_layout_tutorial
    git checkout -b configure-map-layout-solution configure-map-layout-solution-|version|

1. Download the sample NextGen data
===================================

1. Download our sample NextGen data: `sample_nextgen_data.zip <https://drive.google.com/file/d/10Q960TiHNer-6cwjPYN_t4KsOX2917Hl/view?usp=share_link>`_
2. Save to :file:`$TETHYS_HOME/workspaces/map_layout_tutorial/app_workspace`
3. Unzip the contents to the same location
4. Delete the zip file

.. tip::
  
  The :file:`app_workspace` folder is the best place to store data that your Tethys app will need to reference.

2. Explore the Data
===================

1. Enter the :file:`sample_nextgen_data` folder and note two subfolders named :file:`config` and :file:`outputs`. 

The :file:`config` folder contains files that are used to configure and run the NextGen model. The :file:`outputs` folder contains the output files generated from the model run.

2. Enter the :file:`outputs` folder

Note that there are nearly 1,000 files in this folder - most of which are in CSV format. These are the time-series outputs of the NextGen model - one per each catchment and nexus that was modeled. The catchment outputs are all named :file:`<catID>.csv` and the nexus outputs are named :file:`<nexID>_output.csv`. You can open up each and take a look at them. We will come back to these files later in the tutorial as we work on being able to dynamically view them within this tutorial's Tethys app.

3. Return to the :file:`sample_nextgen_data` folder

4. Enter the :file:`config` folder

Note the various file formats (i.e. suffixes). The only files of interest to us are those ending in :file:`.geojson`, representing the GeoJSON format. GeoJSON is a standardized, spatial data format used to represent the locations and shapes of features on the earth. Some inputs to the NextGen model fall under this category: namely, the nexus points, flowpaths and catchments. Note that there is a :file:`.geojson` file containing the spatial data for each of these datasets: :file:`nexus.geojson`, :file:`flowpaths.geojson`, and :file:`catchments.geojson`

.. tip::

  You can learn more about GeoJSON on `the official website <https://geojson.org/>`_.

6. Open the :file:`nexus.geojson` file

Any editor will do. 

7. Note the coordinate reference system

This is found under the path ``crs > properties > name`` and shows ``urn:ogc:def:crs:EPSG::5070``. The most common projections for web-mapping (including Tethys) are ``EPSG:4326`` (i.e. ``WGS84``) and ``EPSG:3857``. We will need ensure that any data we intend to visualize in our Tethys application is in one of these formats into one of these formats. We'll go with ``EPSG:4326``.

3. Reproject the Spatial Data
=============================

There are various packages and tools out there that can be used to reproject spatial datasets. The most straightforward option is to use ``geopandas``. To do this, we will create a small command-line python script that can reproject any provided GeoJSON file into the provided projection.

1. Create a subfolder in the :file:`~/tethysdev/tethysapp-map_layout_tutorial` folder called :file:`scripts`.

2. Enter this new :file:`scripts` folder

3. Create a file called :file:`reproject_environment.yml`.

This file will define the conda environment required to run the reproject script we will create.

4. Paste the following into the file:

.. code-block:: yaml

  name: reproject
  channels:
    - conda-forge
  dependencies:
    - python >=3.11
    - geopandas

5. Save and close this file

6. Create another file called :file:`reproject.py`.

This file will contain the actual logic that performs the reprojection.

7. Paste the following into the file:

.. code-block:: python

  import argparse
  import geopandas as gp

  def main(args):
      gp.read_file(args.in_filename).to_crs(f'EPSG:{args.projection}').to_file(args.in_filename.replace('.geojson', f'_{args.projection}.geojson'))

  if __name__ == '__main__':
      parser = argparse.ArgumentParser(
          prog='reproject',
          description='Reproject GeoJSON files.'
      )

      parser.add_argument('in_filename', help='The source GeoJSON file to reproject.')
      parser.add_argument('projection', help='EPSG code of target projection.')

      args = parser.parse_args()
      main(args)

The ``argparse`` library is used to provide useful command-line management to your script, such as argument parsing, basic error handling and help messages. This logic actually takes up the bulk of the script, as can be seen.

The ``geopandas`` library is a powerful library for interacting with spatial data in various formats. Note that the main logic that performs the reprojection is contained on a single line. The GeoJSON file is read into memory, reprojected, and then written back out to a new GeoJSON file.

8. Save and close this file

7. Open the Anaconda Prompt application

8. Create and activate the reproject environment

.. code-block:: bash

  cd ~/tethysdev/tethysapp-map_layout_tutorial/scripts
  conda env create -f reproject_environment.yml
  conda activate reproject

This will create the conda/python environment for executing your script and then make it the active environment.

9. Run the reprojection script on the catchment and nexus datasets

.. code-block:: bash

  python reproject.py $TETHYS_HOME/workspaces/map_layout_tutorial/app_workspace/sample_nextgen_data/config/nexus.geojson 4326
  python reproject.py $TETHYS_HOME/workspaces/map_layout_tutorial/app_workspace/sample_nextgen_data/config/catchments.geojson 4326

And that's it! These GeoJSON files have now been reprojected into ``EPSG:4326`` and are saved alongside the original versions with a ``_4326`` identifier. These are now ready for use in your Tethys web application!

4. Solution
===========

This concludes the Data Prep portion of the Map Layout Tutorial. You can view the solution on GitHub at `<https://github.com/tethysplatform/tethysapp-map_layout_tutorial/tree/data-prep-solution>`_ or clone it as follows:

.. parsed-literal::

    git clone https://github.com/tethysplatform/tethysapp-map_layout_tutorial
    cd tethysapp-map_layout_tutorial
    git checkout -b data-prep-solution data-prep-solution-|version|

You'll also need to do the following:

1. Download the solution version of the sample NextGen data used in this tutorial: `sample_nextgen_data_solution.zip <https://drive.google.com/file/d/1HA6fF_EdGtiE5ceKF0wH2H8GDElMA3zM/view?usp=share_link>`_.
2. Save to :file:`$TETHYS_HOME/workspaces/map_layout_tutorial/app_workspace`
3. Unzip the contents to the same location
4. Delete the zip file
5. Rename the :file:`sample_nextgen_data_solution` to :file:`sample_nextgen_data` (i.e. remove "_solution")
