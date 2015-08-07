"""
********************************************************************************
* Name: map_view.py
* Author: Nathan Swain
* Created On: May 2015
* Copyright: (c) Brigham Young University 2015
* License: BSD 2-Clause
********************************************************************************
"""
from .base import TethysGizmoOptions, SecondaryGizmoOptions

__all__ = ['MapView', 'MVDraw', 'MVView', 'MVLayer', 'MVLegendClass']


class MapView(TethysGizmoOptions):
    """
    The Map View gizmo can be used to produce interactive maps of spatial data. It is powered by OpenLayers 3, a free and open source pure javascript mapping library. It supports layers in a variety of different formats including WMS, Tiled WMS, GeoJSON, KML, and ArcGIS REST. It includes drawing capabilities and the ability to create a legend for the layers included in the map.

    Shapes that are drawn on the map by users can be retrieved from the map via a hidden text field named 'geometry' and it is updated every time the map is changed. The text in the text field is a string representation of JSON. The geometry definition contained in this JSON can be formatted as either GeoJSON or Well Known Text. This can be configured via the output_format option of the MVDraw object. If the Map View is embedded in a form, the geometry that is drawn on the map will automatically be submitted with the rest of the form via the hidden text field.

    Attributes:
        height(str): Height of the map element. Any valid css unit of length (e.g.: '500px'). Defaults to '520px'.
        width(str): Width of the map element. Any valid css unit of length (e.g.: '100%'). Defaults to '100%'.
        basemap(str or dict): The base map to dispaly: either OpenStreetMap, MapQuest, or a Bing map. Valid values for the string option are: 'OpenStreetMap' and 'MapQuest'. If you wish to configure the base map with options, you must use the dictionary form. The dictionary form is required to use a Bing map, because an API key must be passed as an option. See below for more detail.
        view(MVView): An MVView object specifying the initial view or extent for the map.
        controls(list): A list of controls to add to the map. The list can be a list of strings or a list of dictionaries. Valid controls are ZoomSlider, Rotate, FullScreen, ScaleLine, ZoomToExtent, and 'MousePosition'. See below for more detail.
        layers(list): A list of MVLayer objects.
        draw(MVDraw): An MVDraw object specifying the drawing options.
        attributes(str): A string representing additional HTML attributes to add to the primary element (e.g. "onclick=run_me();").
        classes(str): Additional classes to add to the primary HTML element (e.g. "example-class another-class").

    **Options Dictionaries**

    Many of the options above will accept dictionaries with additional options. These dictionaries should be structured with a single key that is the name of the original option with a value of another dictionary containing the additional options. For example, to provide additional options for the 'ZoomToExtent' control, you would create a dictionary with key 'ZoomToExtent' and value of a dictionary with the additional options like this:

    ::

        {'ZoomToExtent': {'projection': 'EPSG:4326', 'extent': [-135, 22, -55, 54]}}

    Most of the additional options correspond with the options objects in the OpenLayers API. The following sections provide links to the OpenLayers objects that you can refer to when selecting the options.

    **Base Maps**

    There are three base maps supported by the Map View gizmo: OpenStreetMap, Bing, and MapQuest. Use the following links to learn about the additional options you can configure the base maps with:

    * Bing: `ol.source.BingMaps <http://openlayers.org/en/v3.5.0/apidoc/ol.source.BingMaps.html>`_
    * MapQuest: `ol.source.MapQuest <http://openlayers.org/en/v3.5.0/apidoc/ol.source.MapQuest.html>`_
    * OpenStreetMap: `ol.source.OSM <http://openlayers.org/en/v3.5.0/apidoc/ol.source.OSM.html>`_

    ::

        {'Bing': {'key': 'Ap|k3yheRE', 'imagerySet': 'Aerial'}}

    **Controls**

    Use the following links to learn about options for the different controls:

    * FullScreen: `ol.control.FullScreen <http://openlayers.org/en/v3.5.0/apidoc/ol.control.FullScreen.html>`_
    * MousePosition: `ol.control.MousePosition <http://openlayers.org/en/v3.5.0/apidoc/ol.control.MousePosition.html>`_
    * Rotate: `ol.control.Rotate <http://openlayers.org/en/v3.5.0/apidoc/ol.control.Rotate.html>`_
    * ScaleLine: `ol.control.ScaleLine <http://openlayers.org/en/v3.5.0/apidoc/ol.control.ScaleLine.html>`_
    * ZoomSlider: `ol.control.ZoomSlider <http://openlayers.org/en/v3.5.0/apidoc/ol.control.ZoomSlider.html>`_
    * ZoomToExtent: `ol.control.ZoomToExtent <http://openlayers.org/en/v3.5.0/apidoc/ol.control.ZoomToExtent.html>`_


    Example

    ::

        # CONTROLLER
        from tethys_sdk.gizmos import MapView, MVDraw, MVView, MVLayer, MVLegendClass

        # Define view options
        view_options = MVView(
            projection='EPSG:4326',
            center=[-100, 40],
            zoom=3.5,
            maxZoom=18,
            minZoom=2
        )

        # Define drawing options
        drawing_options = MVDraw(
            controls=['Modify', 'Move', 'Point', 'LineString', 'Polygon', 'Box'],
            initial='Point',
            output_format='WKT'
        )

        # Define GeoJSON layer
        geojson_object = {
          'type': 'FeatureCollection',
          'crs': {
            'type': 'name',
            'properties': {
              'name': 'EPSG:3857'
            }
          },
          'features': [
            {
              'type': 'Feature',
              'geometry': {
                'type': 'Point',
                'coordinates': [0, 0]
              }
            },
            {
              'type': 'Feature',
              'geometry': {
                'type': 'LineString',
                'coordinates': [[4e6, -2e6], [8e6, 2e6]]
              }
            },
            {
              'type': 'Feature',
              'geometry': {
                'type': 'Polygon',
                'coordinates': [[[-5e6, -1e6], [-4e6, 1e6], [-3e6, -1e6]]]
              }
            }
          ]
        }

        geojson_layer = MVLayer(source='GeoJSON',
                                options=geojson_object,
                                legend_title='Test GeoJSON',
                                legend_extent=[-46.7, -48.5, 74, 59],
                                legend_classes=[
                                    MVLegendClass('polygon', 'Polygons', fill='rgba(255,255,255,0.8)', stroke='#3d9dcd'),
                                    MVLegendClass('line', 'Lines', stroke='#3d9dcd')
                                ])

        # Define GeoServer Layer
        geoserver_layer = MVLayer(source='ImageWMS',
                                  options={'url': 'http://192.168.59.103:8181/geoserver/wms',
                                           'params': {'LAYERS': 'topp:states'},
                                           'serverType': 'geoserver'},
                                  legend_title='USA Population',
                                  legend_extent=[-126, 24.5, -66.2, 49],
                                  legend_classes=[
                                      MVLegendClass('polygon', 'Low Density', fill='#00ff00', stroke='#000000'),
                                      MVLegendClass('polygon', 'Medium Density', fill='#ff0000', stroke='#000000'),
                                      MVLegendClass('polygon', 'High Density', fill='#0000ff', stroke='#000000')
                                  ])

        # Define KML Layer
        kml_layer = MVLayer(source='KML',
                            options={'url': '/static/tethys_gizmos/data/model.kml'},
                            legend_title='Park City Watershed',
                            legend_extent=[-111.60, 40.57, -111.43, 40.70],
                            legend_classes=[
                                MVLegendClass('polygon', 'Watershed Boundary', fill='#ff8000'),
                                MVLegendClass('line', 'Stream Network', stroke='#0000ff'),
                            ])

        # Tiled ArcGIS REST Layer
        arc_gis_layer = MVLayer(source='TileArcGISRest',
                                options={'url': 'http://sampleserver1.arcgisonline.com/ArcGIS/rest/services/' + 'Specialty/ESRI_StateCityHighway_USA/MapServer'},
                                legend_title='ESRI USA Highway',
                                legend_extent=[-173, 17, -65, 72])

        # Define map view options
        map_view_options = MapView(
                height='600px',
                width='100%',
                controls=['ZoomSlider', 'Rotate', 'FullScreen',
                          {'MousePosition': {'projection': 'EPSG:4326'}},
                          {'ZoomToExtent': {'projection': 'EPSG:4326', 'extent': [-130, 22, -65, 54]}}],
                layers=[geojson_layer, geoserver_layer, kml_layer, arc_gis_layer],
                view=view_options,
                basemap='OpenStreetMap',
                draw=drawing_options,
                legend=True
        )

        # TEMPLATE

        {% gizmo map_view map_view_options %}

    """

    def __init__(self, height='100%', width='100%', basemap='OpenStreetMap', view={'center': [-100, 40], 'zoom': 2},
                 controls=[], layers=[], draw=None, legend=False, attributes='', classes=''):
        """
        Constructor
        """
        # Initialize super class
        super(MapView, self).__init__(attributes=attributes, classes=classes)

        self.height = height
        self.width = width
        self.basemap = basemap
        self.view = view
        self.controls = controls
        self.layers = layers
        self.draw = draw
        self.legend = legend


class MVView(SecondaryGizmoOptions):
    """
    MVView objects are used to define the initial view of the Map View. The initial view is set by specifying a center and a zoom level.

    Attributes:
        projection(str): Projection of the center coordinates given. This projection will be used to transform the coordinates into the default map projection (EPSG:3857).
        center(list): An array with the coordinates of the center point of the initial view.
        zoom(int or float): The zoom level for the initial view.
        maxZoom(int or float): The maximum zoom level allowed. Defaults to 28.
        minZoom(int or float): The minimum zoom level allowed. Defaults to 0.

    Example

    ::

        view_options = MVView(
            projection='EPSG:4326',
            center=[-100, 40],
            zoom=3.5,
            maxZoom=18,
            minZoom=2
        )

    """

    def __init__(self, projection, center, zoom, maxZoom=28, minZoom=0):
        """
        Constructor
        """
        # Initialize super class
        super(MVView, self).__init__()

        self.projection = projection
        self.center = center
        self.zoom = zoom
        self.maxZoom = maxZoom
        self.minZoom = minZoom


class MVDraw(SecondaryGizmoOptions):
    """
    MVDraw objects are used to define the drawing options for Map View.

    Attributes:
        controls(list, required): List of drawing controls to add to the map. Valid options are 'Modify', 'Move', 'Point', 'LineString', 'Polygon' and 'Box'.
        initial(str, required): Drawing control to be enabled initially. Must be included in the controls list.
        output_format(str): Format to output to the hidden text area. Either 'WKT' (for Well Known Text format) or 'GeoJSON'. Defaults to 'GeoJSON'

    Example

    ::

        drawing_options = MVDraw(
            controls=['Modify', 'Move', 'Point', 'LineString', 'Polygon', 'Box'],
            initial='Point',
            output_format='WKT'
        )

    """

    def __init__(self, controls, initial, output_format='GeoJSON'):
        """
        Constructor
        """
        # Initialize super class
        super(MVDraw, self).__init__()

        self.controls = controls

        # Validate initial
        if initial not in self.controls:
            raise ValueError('Value of "initial" must be contained in the "controls" list.')
        self.initial = initial
        self.output_format = output_format


class MVLayer(SecondaryGizmoOptions):
    """
    MVLayer objects are used to define map layers for the Map View Gizmo.

    Attributes:
        source (str, required): The source or data type of the layer (e.g.: ImageWMS)
        options (dict, required): A dictionary representation of the OpenLayers layer options object for the source.
        legend_title (str, required): The human readable name of the layer that will be displayed in the legend.
        legend_classes (list): A list of MVLegendClass objects.
        legend_extent (list): A list of four ordinates representing the extent that will be used on "zoom to layer": [minx, miny, maxx, maxy].
        legend_extent_projection (str): The EPSG projection of the extent coordinates. Defaults to "EPSG:4326".

    Example

    ::

        # Define GeoJSON layer
        geojson_object = {
          'type': 'FeatureCollection',
          'crs': {
            'type': 'name',
            'properties': {
              'name': 'EPSG:3857'
            }
          },
          'features': [
            {
              'type': 'Feature',
              'geometry': {
                'type': 'Point',
                'coordinates': [0, 0]
              }
            },
            {
              'type': 'Feature',
              'geometry': {
                'type': 'LineString',
                'coordinates': [[4e6, -2e6], [8e6, 2e6]]
              }
            },
            {
              'type': 'Feature',
              'geometry': {
                'type': 'Polygon',
                'coordinates': [[[-5e6, -1e6], [-4e6, 1e6], [-3e6, -1e6]]]
              }
            }
          ]
        }

        geojson_layer = MVLayer(source='GeoJSON',
                                options=geojson_object,
                                legend_title='Test GeoJSON',
                                legend_extent=[-46.7, -48.5, 74, 59],
                                legend_classes=[
                                    MVLegendClass('polygon', 'Polygons', fill='rgba(255,255,255,0.8)', stroke='#3d9dcd'),
                                    MVLegendClass('line', 'Lines', stroke='#3d9dcd')
                                ])

        # Define GeoServer Layer
        geoserver_layer = MVLayer(source='ImageWMS',
                                  options={'url': 'http://192.168.59.103:8181/geoserver/wms',
                                           'params': {'LAYERS': 'topp:states'},
                                           'serverType': 'geoserver'},
                                  legend_title='USA Population',
                                  legend_extent=[-126, 24.5, -66.2, 49],
                                  legend_classes=[
                                      MVLegendClass('polygon', 'Low Density', fill='#00ff00', stroke='#000000'),
                                      MVLegendClass('polygon', 'Medium Density', fill='#ff0000', stroke='#000000'),
                                      MVLegendClass('polygon', 'High Density', fill='#0000ff', stroke='#000000')
                                  ])

        # Define KML Layer
        kml_layer = MVLayer(source='KML',
                            options={'url': '/static/tethys_gizmos/data/model.kml'},
                            legend_title='Park City Watershed',
                            legend_extent=[-111.60, 40.57, -111.43, 40.70],
                            legend_classes=[
                                MVLegendClass('polygon', 'Watershed Boundary', fill='#ff8000'),
                                MVLegendClass('line', 'Stream Network', stroke='#0000ff'),
                            ])

        # Tiled ArcGIS REST Layer
        arc_gis_layer = MVLayer(source='TileArcGISRest',
                                options={'url': 'http://sampleserver1.arcgisonline.com/ArcGIS/rest/services/' + 'Specialty/ESRI_StateCityHighway_USA/MapServer'},
                                legend_title='ESRI USA Highway',
                                legend_extent=[-173, 17, -65, 72]),
    """

    def __init__(self, source, options, legend_title, legend_classes=None, legend_extent=None, legend_extent_projection='EPSG:4326'):
        """
        Constructor
        """
        super(MVLayer, self).__init__()

        self.source = source
        self.legend_title = legend_title
        self.options = options
        self.legend_classes = legend_classes
        self.legend_extent = legend_extent
        self.legend_extent_projection = legend_extent_projection


class MVLegendClass(SecondaryGizmoOptions):
    """
    MVLegendClasses are used to define the classes listed in the legend.

    Attributes:
        type (str, required): The type of feature to be represented by the legend class. Either 'point', 'line', 'polygon', or 'raster'.
        value (str, required): The value or name of the legend class.
        fill (str): Valid RGB color for the fill (e.g.: '#00ff00', 'rgba(0, 255, 0, 0.5)'). Required for 'point' or 'polygon' types.
        stoke (str): Valid RGB color for the stoke/line (e.g.: '#00ff00', 'rgba(0, 255, 0, 0.5)'). Required for 'line' types and optional for 'polygon' types.
        ramp (list): A list of hexidecimal RGB colors that will be used to construct a color ramp. Required for 'raster' types.

    Example

    ::

        point_class = MVLegendClass(type='point', value='Cities', fill='#00ff00')
        line_class = MVLegendClass(type='line', value='Roads', stroke='rbga(0,0,0,0.7)')
        polygon_class = MVLegendClass(type='polygon', value='Lakes', stroke='#0000aa', fill='#0000ff')

    """

    def __init__(self, type, value, fill='', stroke='', ramp=[]):
        """
        Constructor
        """

        # Initialize super class
        super(MVLegendClass, self).__init__()

        self.POINT_TYPE = 'point'
        self.LINE_TYPE = 'line'
        self.POLYGON_TYPE = 'polygon'
        self.RASTER_TYPE = 'raster'
        self.VALID_TYPES = [self.POINT_TYPE, self.LINE_TYPE, self.POLYGON_TYPE, self.RASTER_TYPE]

        if type not in self.VALID_TYPES:
            raise ValueError('"{0}" is not a valid MVLegendClass type. Use either '
                             '"point", "line", "polygon", or "raster".'.format(type))

        self.type = type
        self.value = value

        if type == self.POINT_TYPE:
            if fill:
                self.fill = fill
            else:
                raise ValueError('Argument "fill" must be specified for MVLegendClass of type "point".')

        elif type == self.LINE_TYPE:
            if stroke:
                self.stroke = stroke
            else:
                raise ValueError('Argument "line" must be specified for MVLegendClass of type "line".')

        elif type == self.POLYGON_TYPE:
            if fill and stroke:
                self.stroke = stroke
                self.fill = fill
            elif fill:
                self.line = fill
                self.fill = fill
            else:
                raise ValueError('Argument "fill" must be specified for MVLegendClass of type "polygon".')

        elif type == self.RASTER_TYPE:
            if ramp:
                self.ramp = ramp
            else:
                raise ValueError('Argument "ramp" must be specified for MVLegendClass of type "raster".')


