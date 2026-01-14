********************
Additional Exercises
********************

**Last Updated:** July 2024

Now that you have completed the Map Layout tutorial, try one of the following exercises on your own to improve the usability of the app:

0. Start From Previous Solution (Optional)
==========================================

If you wish to use the previous solution as a starting point:

.. parsed-literal::

    git clone https://github.com/tethysplatform/tethysapp-map_layout_tutorial
    cd tethysapp-map_layout_tutorial
    git checkout -b configure-data-plotting-solution configure-data-plotting-solution-|version|

You'll also need to do the following:

1. Download the solution version of the sample NextGen data used in this tutorial: `sample_nextgen_data_solution.zip <https://drive.google.com/file/d/1HA6fF_EdGtiE5ceKF0wH2H8GDElMA3zM/view?usp=share_link>`_.
2. Save to :file:`$TETHYS_HOME/workspaces/map_layout_tutorial/app_workspace`
3. Unzip the contents to the same location
4. Delete the zip file
5. Rename the :file:`sample_nextgen_data_solution` to :file:`sample_nextgen_data` (i.e. remove "_solution")

1. Add the flowpath data
========================

If you are familiar with the NextGen model outputs - or if you noticed during the Data Prep section, there was a :file:`flowpaths.geojson` file in the :file:`config` folder and a :file:`flowveldepth_HY_Features Test.csv` file in the :file:`outputs` folder. Try to tackle incorporating these into your app in the same way we did with the catchment and nexus data.

Good luck!

