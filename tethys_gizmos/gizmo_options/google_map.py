from .base import TethysGizmoOptions

__all__ = ['GoogleMapView']


class GoogleMapView(TethysGizmoOptions):
    """
    Google Map View

    The Google Map View is similar to Map View, but it is powered by Google Maps 3. It has the drawing library enabled to allow geospatial user input. An optional background dataset can be specified for reference, but only the shapes drawn by the user are returned (see `Retrieving Shapes reference <http://127.0.0.1:8000/developer/gizmos/#retrieving_shapes>`_ section).

    Attributes
    height(string, required): Height of map container in normal css units
    width(string, required): Width of map container in normal css units
    maps_api_key(string, required): The Google Maps API key. If the API key is provided in the settings.py via the TETHYS_GIZMOS_GOOGLE_MAPS_API_KEY option, this parameter is not required.
    reference_kml_action(url string): The action that returns the background kml datasets. These datasets are used for reference only.
    drawing_types_enabled(list of strings): A list of the types of geometries the user will be allowed to draw (POLYGONS, POINTS, POLYLINES).
    initial_drawing_mode(string): A string representing the drawing mode that will be enabled by default. Valid modes are: 'POLYGONS', 'POINTS', 'POLYLINES'. The mode used must be one of the drawing_types_enabled that the user is allowed to draw.
    output_format(string): A string specifying the format of the string that is output by the editable map tool. Valid values are 'GEOJSON' for GeoJSON format or 'WKT' for Well Known Text Format.
    input_overlays(PySON): A JavaScript-equivilent Python data structure representing GeoJSON or WktJSON containing the geometry and attributes to be added to the map as overlays (see example below). Only points, lines and polygons are supported.
    """

    def __init__(self, height, width, maps_api_key="", reference_kml_action="", drawing_types_enabled=[], initial_drawing_mode="", output_format='GEOJSON', input_overlays=[None]):
        """
        Constructor
        """
        # Initialize super class
        super(GoogleMapView, self).__init__()

        self.height = height
        self.width = width
        self.maps_api_key = maps_api_key
        self.reference_kml_action = reference_kml_action
        self.drawing_types_enabled = drawing_types_enabled
        self.initial_drawing_mode = initial_drawing_mode
        self.output_format = output_format
        self.input_overlays = input_overlays