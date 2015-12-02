"""
********************************************************************************
* Name: google_map.py
* Author: Nathan Swain
* Created On: May 2015
* Copyright: (c) Brigham Young University 2015
* License: BSD 2-Clause
********************************************************************************
"""
from .base import TethysGizmoOptions

__all__ = ['GoogleMapView']


class GoogleMapView(TethysGizmoOptions):
    """
    Google Map View

    The Google Map View is similar to Map View, but it is powered by Google Maps 3. It has the drawing library enabled to allow geospatial user input. An optional background dataset can be specified for reference, but only the shapes drawn by the user are returned (see `Retrieving Shapes reference <http://127.0.0.1:8000/developer/gizmos/#retrieving_shapes>`_ section).

    Shapes that are drawn on the map by users can be retrieved from the map in two ways. A hidden text field named 'geometry' is updated every time the map is changed. The text in the text field is a string representation of JSON. The geometry can be formatted as either GeoJSON or Well Known Text. This can be configured by setting the output_format parameter. If the Google Map View is embedded in a form, the geometry that is drawn on the map will automatically be submitted with the rest of the form via the hidden text field.

    Alternatively, the data can be extracted directly using the JavaScript API (see below).

    Attributes
        height(string, required): Height of map container in normal css units
        width(string, required): Width of map container in normal css units
        maps_api_key(string, required): The Google Maps API key. If the API key is provided in the settings.py via the TETHYS_GIZMOS_GOOGLE_MAPS_API_KEY option, this parameter is not required.
        reference_kml_action(url string): The action that returns the background kml datasets. These datasets are used for reference only.
        drawing_types_enabled(list of strings): A list of the types of geometries the user will be allowed to draw (POLYGONS, POINTS, POLYLINES).
        initial_drawing_mode(string): A string representing the drawing mode that will be enabled by default. Valid modes are: 'POLYGONS', 'POINTS', 'POLYLINES'. The mode used must be one of the drawing_types_enabled that the user is allowed to draw.
        output_format(string): A string specifying the format of the string that is output by the editable map tool. Valid values are 'GEOJSON' for GeoJSON format or 'WKT' for Well Known Text Format.
        input_overlays(PySON): A JavaScript-equivalent Python data structure representing GeoJSON or WktJSON containing the geometry and attributes to be added to the map as overlays (see example below). Only points, lines and polygons are supported.
        attributes(dict): A dictionary representing additional HTML attributes to add to the primary element (e.g. {"onclick": "run_me();"}).
        classes(str): Additional classes to add to the primary HTML element (e.g. "example-class another-class").


    Example

    ::

        # CONTROLLER
        from tethys_sdk.gizmos import GoogleMapView

        google_map_view = GoogleMapView(height='600px',
                                        width='100%',
                                        reference_kml_action=reverse('gizmos:get_kml'),
                                        drawing_types_enabled=['POLYGONS', 'POINTS', 'POLYLINES'],
                                        initial_drawing_mode='POINTS',
                                        output_format='WKT')

        # GeoJSON Example
        geo_json = {'type':'WKTGeometryCollection',
            'geometries':[
                          {'type':'Point',
                           'wkt':'POINT(-111.5123462677002 40.629197012613545)',
                           'properties':{'id':1,'value':1}
                           },
                          {'type':'Polygon',
                           'wkt':'POLYGON((-111.50153160095215 40.63193284946615, -111.50101661682129 40.617210120505035, -111.48625373840332 40.623594711231775, -111.49123191833496 40.63193284946615, -111.50153160095215 40.63193284946615))',
                           'properties':{'id':2,'value':2}
                           },
                          {'type':'PolyLine',#
                           'wkt':'POLYLINE(-111.49123191833496 40.65003865742191, -111.49088859558105 40.635319920747456, -111.48127555847168 40.64912697157757, -111.48024559020996 40.634668574229735)',
                           'properties':{'id':3,'value':3}
                           }
                          ]
            }

        google_map_view_options = {'height': '700px',
                                   'width': '100%',
                                   'maps_api_key': 'S0mEaPIk3y',
                                   'drawing_types_enabled': ['POLYGONS', 'POINTS', 'POLYLINES'],
                                   'initial_drawing_mode': 'POINTS',
                                   'input_overlays': geo_json}

        # WKT Example

        wkt_json = {"type":"GeometryCollection",
            "geometries":[
                          {"type":"Point",
                           "coordinates":[40.629197012613545,-111.5123462677002],
                           "properties":{"id":1,"value":1}},
                          {"type":"Polygon",
                           "coordinates":[[40.63193284946615,-111.50153160095215],[40.617210120505035,-111.50101661682129],[40.623594711231775,-111.48625373840332],[40.63193284946615,-111.49123191833496]],
                           "properties":{"id":2,"value":2}},
                          {"type":"LineString",
                           "coordinates":[[40.65003865742191,-111.49123191833496],[40.635319920747456,-111.49088859558105],[40.64912697157757,-111.48127555847168],[40.634668574229735,-111.48024559020996]],
                           "properties":{"id":3,"value":3}}
                          ]
            }

        google_map_view_options = {'height': '700px',
                                   'width': '100%',
                                   'maps_api_key': 'S0mEaPIk3y',
                                   'drawing_types_enabled': ['POLYGONS', 'POINTS', 'POLYLINES'],
                                   'initial_drawing_mode': 'POINTS',
                                   'input_overlays': wkt_json}

        # TEMPLATE

        {% gizmo google_map_view google_map_view_options %}

    """

    def __init__(self, height, width, maps_api_key="", reference_kml_action="", drawing_types_enabled=[],
                 initial_drawing_mode="", output_format='GEOJSON', input_overlays=[None], attributes={}, classes=''):
        """
        Constructor
        """
        # Initialize super class
        super(GoogleMapView, self).__init__(attributes=attributes, classes=classes)

        self.height = height
        self.width = width
        self.maps_api_key = maps_api_key
        self.reference_kml_action = reference_kml_action
        self.drawing_types_enabled = drawing_types_enabled
        self.initial_drawing_mode = initial_drawing_mode
        self.output_format = output_format
        self.input_overlays = input_overlays