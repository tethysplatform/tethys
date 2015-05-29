**************
The Controller
**************

**Last Updated:** May 20, 2015

The Controller component of MVC will be discussed in this part of the tutorial. The job of the controller is to coordinate between the View and the Model. Often this means querying a database and transforming the data to a format that the view expects it to be in. The Controller also handles most of the application logic such as processing and validating form data or launching model runs. In a Tethys app, controllers are simple Python functions.

Django is used to implement Tethys controllers but they are called "views" in Django. The `Writing Views <https://docs.djangoproject.com/en/1.7/topics/http/views/>`_ documentation for Django is a good reference for Tethys controllers. Note that URL mapping is handled differently in Tethys app development than in Django development and will be discussed in the :doc:`./url_mapping` tutorial.

In this tutorial you will write a controller that will retrieve the data from your stream gage model and then pass it to the template that you created in the previous tutorial.

Make a New Controller
=====================

Recall that in :doc:`./model` tutorial you created an SQLAlchemy data model to store information about stream gages. You also created an initialization function that loaded some dummy data into your database. You will now add some logic to your controller to retrieve this data and pass it to the template.

Open your :file:`controllers.py` file located at :file:`my_first_app/controllers.py`. This file should contain a function called ``home``. This function is the controller for the home page of your app. All controller functions must accept a request object and they must return a response object. The request object contains information about the HTTP request, including any form data that is submitted (more on this later). There are several ways to return a response object, but the most common way is to use the ``render()`` function provided by Django. This function requires three arguments: the request object, the template to be rendered, and the context dictionary.

Add the following imports to the top of the file:

::

    from .model import SessionMaker, StreamGage
    from tethys_gizmos.gizmo_options import MapView, MVLayer, MVView

Then add a new controller function called ``map`` after the ``home`` function:

::

    def map(request):
        """
        Controller for map page.
        """
        # Create a session
        session = SessionMaker()

        # Query DB for gage objects
        gages = session.query(StreamGage).all()

        # Transform into GeoJSON format
        features = []

        for gage in gages:
            gage_feature = {
              'type': 'Feature',
              'geometry': {
                'type': 'Point',
                'coordinates': [gage.longitude, gage.latitude]
              }
            }

            features.append(gage_feature)

        geojson_gages = {
          'type': 'FeatureCollection',
          'crs': {
            'type': 'name',
            'properties': {
              'name': 'EPSG:4326'
            }
          },
          'features': features
        }

        # Define layer for Map View
        geojson_layer = MVLayer(source='GeoJSON',
                                options=geojson_gages,
                                legend_title='Provo Stream Gages',
                                legend_extent=[-111.74, 40.22, -111.67, 40.25])

        # Define initial view for Map View
        view_options = MVView(
            projection='EPSG:4326',
            center=[-100, 40],
            zoom=3.5,
            maxZoom=18,
            minZoom=2
        )

        # Configure the map
        map_options = MapView(height='500px',
                              width='100%',
                              layers=[geojson_layer],
                              view=view_options,
                              basemap='OpenStreetMap',
                              legend=True)

        # Pass variables to the template via the context dictionary
        context = {'map_options': map_options}

        return render(request, 'my_first_app/map.html', context)



The new ``map`` controller queries the persistent store for the stream gages, converts the data into `GeoJSON <http://geojson.org/>`_ format for the map, and configures the map options for the Map View Gizmo that is used in the template.

To query the database, an SQLAlchemy ``session`` object is needed. It is created using the ``SessionMaker`` object imported from the :file:`model.py` file. Querying is accomplished by using the ``query()`` method on the ``session`` object. The result is a list of ``StreamGage`` objects representing the records in the database.

The map is capable of consuming spatial data in a few formats including GeoJSON, so the ``map`` controller handles the job of converting the data from the list of ``StreamGage`` objects to GeoJSON format.

The map Gizmo that is used in the :file:`map.html` template requires a dictionary of configuration options called "map_options". This is created in the controller and the ``input_overlays`` option is used to give the GeoJSON formatted stream gage data to the map.

Next, a template context dictionary is defined that contains all of the variables that you wish to be available for use in the template.

Finally, the ``render()`` function is used to create the response object. It is in the ``render()`` function that you specify the template that is to be rendered by the controller. In this case, the :file:`map.html` that you created in the last tutorial. Note that the path you provide to the template is relative to the template directory of your app: ``my_first_app/map.html``.

Save :file:`controllers.py` before going on.

