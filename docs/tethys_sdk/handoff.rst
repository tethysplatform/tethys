***********
Handoff API
***********

**Last Updated:** October 14, 2015

App developers can use Handoff to launch one app from another app or an external website. Handoff also provides a mechanism for passing data from the originator app to the target app. Using Handoff, apps can be strung together to form a workflow, allowing apps to become modular and specialized in their capabilities.

As an example, consider an app called "Hydrograph Plotter" that plots hydrographs. We would like Hydrograph Plotter to be able to accept hydrograph CSV files from other apps so that it can be used as a generic hydrograph viewer. One way to do this would be to define a Handoff endpoint that accepts a URL to a CSV file. The Handoff handler would use that URL to download or pull the CSV file into the app and then redirect it to a page with a plot. The GET request/pull mechanism is used to get around the limitations associated with POST requests, which are required to push or upload files.

Create a Handoff Handler
------------------------

The first step is to define a Handoff handler. The purpose of the Handoff handler is to handle the transfer data from the originator and then redirect the call to a page in the target app. It is implemented as a function that returns a URL or name of a view. For the example, the Handoff handler could be defined as follows:

::

    import os
    import requests
    from .app import HydrographPlotter

    def csv(request, csv_url):
        """
        Handoff handler for csv files.
        """
        # Get a filename in the current user's workspace
        user_workspace = HydrographPlotter.get_user_workspace(request.user)
        filename = os.path.join(user_workspace, 'hydrograph.csv')

        # Initiate a GET request on the CSV URL
        response = requests.get(csv_url, stream=True)

        # Stream content into a file
        with open(filename, 'w') as f:
            for chunk in response.iter_content(chunk_size=512):
                if chunk:
                    f.write(chunk)

        return 'hydrograph_plotter:plot_csv'

This Handoff handler uses the ``requests`` library and the :doc:`./workspaces` to download the file and store it in the current user's workspace. Then it returns the name of a controller called ``plot_csv`` to be redirected to. The ``plot_csv`` controller would need to know to look for a file in the current user's workspace and plot it.


Register Handoff Handler
------------------------

The Handoff handler needs to be registered to make it available for other apps to use. This is done by adding the ``handoff_handlers`` method to the :term:`app class`. This method needs to return a list or tuple of ``HandoffHandler`` objects.

::

    from tethys_sdk.handoff import HandoffHandler

    class HydrographPlotter(TethysAppBase):
        """
        Tethys app class for Hydrograph Plotter
        """
        ...

        def handoff_handlers(self):
            """
            Register some handoff handlers
            """
            handoff_handlers = (HandoffHandler(name='plot-csv',
                                               handler='app_name.handoff.csv'),
            )
            return handoff_handlers



Execute a Handoff
-----------------

To execute a Handoff, the originator app or website needs to provide a link of the form:

::

    http://<host>/handoff/<app_name>/<handler_name>/?param1=x&param2=y

Any parameters that need to be passed with the Handoff call are passed as query parameters on the URL. For our example, the URL would look something like this:

::

    http://www.example.com/hydrograph-plotter/plot-csv/?csv=http://www.another.com/url/to/file.csv

The URL must have query parameters for each argument defined in the Handoff handler function or it will throw an error. It will also throw an error if extra query parameters are provided that are not defined as arguments for the Handoff handler function.

View Handoff Endpoints for Apps
-------------------------------

For convenience, a list of the available Handoff endpoints for an app can be viewed by visiting the URL:

::

    http://<host>/handoff/<app_name>/

For our example, the URL would look like this:

::

    http://www.example.com/handoff/hydrograph-plotter/

The output would look something like this:

::

    [{"arguments": ["csv"], "name": "plot-csv"}]





