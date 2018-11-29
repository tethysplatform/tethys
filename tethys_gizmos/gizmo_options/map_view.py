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
from django.conf import settings
import logging
log = logging.getLogger('tethys.tethys_gizmos.gizmo_options.map_view')

__all__ = ['MapView', 'MVDraw', 'MVView', 'MVLayer',
           'MVLegendClass', 'MVLegendImageClass', 'MVLegendGeoServerImageClass']


class MapView(TethysGizmoOptions):
    """
    The Map View gizmo can be used to produce interactive maps of spatial data. It is powered by OpenLayers, a free and open source pure javascript mapping library. It supports layers in a variety of different formats including WMS, Tiled WMS, GeoJSON, KML, and ArcGIS REST. It includes drawing capabilities and the ability to create a legend for the layers included in the map.

    Shapes that are drawn on the map by users can be retrieved from the map via a hidden text field named 'geometry' and it is updated every time the map is changed. The text in the text field is a string representation of JSON. The geometry definition contained in this JSON can be formatted as either GeoJSON or Well Known Text. This can be configured via the output_format option of the MVDraw object. If the Map View is embedded in a form, the geometry that is drawn on the map will automatically be submitted with the rest of the form via the hidden text field.

    Attributes:
        height(str): Height of the map element. Any valid css unit of length (e.g.: '500px'). Defaults to '520px'.
        width(str): Width of the map element. Any valid css unit of length (e.g.: '100%'). Defaults to '100%'.
        basemap(str, dict or a list of strings and/or dicts): The base maps to display: choose from OpenStreetMap, MapQuest, or a Bing map. Valid values for the string option are: 'OpenStreetMap' and 'MapQuest'. If you wish to configure the base map with options, you must use the dictionary form. The dictionary form is required to use a Bing map, because an API key must be passed as an option. See below for more detail. A basemap switcher will automatically be provided if a list of more than one basemap is included.
        view(MVView): An MVView object specifying the initial view or extent for the map.
        controls(list): A list of controls to add to the map. The list can be a list of strings or a list of dictionaries. Valid controls are ZoomSlider, Rotate, FullScreen, ScaleLine, ZoomToExtent, and 'MousePosition'. See below for more detail.
        layers(list): A list of MVLayer objects.
        draw(MVDraw): An MVDraw object specifying the drawing options.
        disable_basemap(bool): Render the map without a base map.
        feature_selection(bool): A dictionary of global feature selection options. See below.
        attributes(dict): A dictionary representing additional HTML attributes to add to the primary element (e.g. {"onclick": "run_me();"}).
        classes(str): Additional classes to add to the primary HTML element (e.g. "example-class another-class").

    **Options Dictionaries**

    Many of the options above will accept dictionaries with additional options. These dictionaries should be structured with a single key that is the name of the original option with a value of another dictionary containing the additional options. For example, to provide additional options for the 'ZoomToExtent' control, you would create a dictionary with key 'ZoomToExtent' and value of a dictionary with the additional options like this:

    ::

        {'ZoomToExtent': {'projection': 'EPSG:4326', 'extent': [-135, 22, -55, 54]}}

    Most of the additional options correspond with the options objects in the OpenLayers API. The following sections provide links to the OpenLayers objects that you can refer to when selecting the options.

    **Base Maps**

    There are several base maps supported by the Map View gizmo: `OpenStreetMap`, `Bing`, `Stamen`, `CartoDB`, and `ESRI`. All base maps can be specified as a string or as an options dictionary. When using an options dictionary all base maps map services accept the option `control_label`, which is used to specify the label to be used in the Base Map control. For example::

        {'Bing': {'key': 'Ap|k3yheRE', 'imagerySet': 'Aerial', 'control_label': 'Bing Aerial'}}

    For additional options that can be provided to each base map service see the following links:

    * OpenStreetMap: `ol/source/OSM <http://openlayers.org/en/latest/apidoc/module-ol_source_OSM-OSM.html>`_
    * Bing: `ol/source/BingMaps <http://openlayers.org/en/latest/apidoc/module-ol_source_BingMaps-BingMaps.html>`_
    * Stamen: `ol/source/Stamen <http://openlayers.org/en/latest/apidoc/module-ol_source_Stamen-Stamen.html>`_
    * XYZ `ol/source/XYZ <http://openlayers.org/en/latest/apidoc/module-ol_source_XYZ-XYZ.html>`_

    .. note::

        The CartoDB and ESRI services are just pre-defined instances of the XYZ service. In addition to the standard XYZ options they have the following additional options:

    CartoDB:
        * `style`: The style of map. Possibilities are 'light' or 'dark'.
        * `labels`: Boolean specifying whether or not to include labels.

    ESRI:
        * `layer`: A string specifying which ESRI map to use. Possibilities are:
            * NatGeo_World_Map
            * Ocean_Basemap
            * USA_Topo_Maps
            * World_Imagery
            * World_Physical_Map
            * World_Shaded_Relief
            * World_Street_Map
            * World_Terrain_Base
            * World_Topo_Map

    **Controls**

    Use the following links to learn about options for the different controls:

    * FullScreen: `ol.control.FullScreen <http://openlayers.org/en/v4.0.1/apidoc/ol.control.FullScreen.html>`_
    * MousePosition: `ol.control.MousePosition <http://openlayers.org/en/v4.0.1/apidoc/ol.control.MousePosition.html>`_
    * Rotate: `ol.control.Rotate <http://openlayers.org/en/v4.0.1/apidoc/ol.control.Rotate.html>`_
    * ScaleLine: `ol.control.ScaleLine <http://openlayers.org/en/v4.0.1/apidoc/ol.control.ScaleLine.html>`_
    * ZoomSlider: `ol.control.ZoomSlider <http://openlayers.org/en/v4.0.1/apidoc/ol.control.ZoomSlider.html>`_
    * ZoomToExtent: `ol.control.ZoomToExtent <http://openlayers.org/en/v4.0.1/apidoc/ol.control.ZoomToExtent.html>`_

    **Feature Selection**

    The feature_selection dictionary contains global settings that can be used to modify the behavior of the feature selection functionality. An explanation of valid options follows:

    * multiselect: Set to True to allow multiple features to be selected while holding the shift key on the keyboard. Defaults to False.
    * sensitivity: Integer value that adjust the feature selection sensitivity. Defaults to 2.

    .. tip::

        **OpenLayers Version**

        Currently, OpenLayers version 5.3.0 is used by default with the Map View gizmo. If you need a specific version of OpenLayers you can specify the version number using the `ol_version` class attribute on the `MapView` class::

            MapView.ol_version = '4.6.5'

        Any versions that are provided by https://www.jsdelivr.com/package/npm/openlayers can be specified.

    Controller Example

    ::

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
            controls=['Modify', 'Delete', 'Move', 'Point', 'LineString', 'Polygon', 'Box'],
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

        # Define GeoJSON point layer
        geojson_point_object = {
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
          ]
        }

        geojson_layer = MVLayer(
            source='GeoJSON',
            options=geojson_object,
            legend_title='Test GeoJSON',
            legend_extent=[-46.7, -48.5, 74, 59],
            legend_classes=[
                MVLegendClass('polygon', 'Polygons', fill='rgba(255,255,255,0.8)', stroke='#3d9dcd'),
                MVLegendClass('line', 'Lines', stroke='#3d9dcd')
            ]
        )

        geojson_point_layer = MVLayer(
            source='GeoJSON',
            options=geojson_point_object,
            legend_title='Test GeoJSON',
            legend_extent=[-46.7, -48.5, 74, 59],
            legend_classes=[
                MVLegendClass('line', 'Lines', stroke='#3d9dcd')
            ],
            layer_options={
                'style': {
                    'image': {
                        'circle': {
                            'radius': 10,
                            'fill': {'color':  '#d84e1f'},
                            'stroke': {'color': '#ffffff', 'width': 1},
                        }
                    }
                }
            }
        )

        # Define GeoServer Layer
        geoserver_layer = MVLayer(
            source='ImageWMS',
            options={'url': 'http://192.168.59.103:8181/geoserver/wms',
                   'params': {'LAYERS': 'topp:states'},
                   'serverType': 'geoserver'},
            legend_title='USA Population',
            legend_extent=[-126, 24.5, -66.2, 49],
            legend_classes=[
                MVLegendClass('polygon', 'Low Density', fill='#00ff00', stroke='#000000'),
                MVLegendClass('polygon', 'Medium Density', fill='#ff0000', stroke='#000000'),
                MVLegendClass('polygon', 'High Density', fill='#0000ff', stroke='#000000')
            ]
        )

        # Define KML Layer
        kml_layer = MVLayer(
            source='KML',
            options={'url': '/static/tethys_gizmos/data/model.kml'},
            legend_title='Park City Watershed',
            legend_extent=[-111.60, 40.57, -111.43, 40.70],
            legend_classes=[
                MVLegendClass('polygon', 'Watershed Boundary', fill='#ff8000'),
                MVLegendClass('line', 'Stream Network', stroke='#0000ff'),
            ]
        )

        # Tiled ArcGIS REST Layer
        arc_gis_layer = MVLayer(
            source='TileArcGISRest',
            options={'url': 'http://sampleserver1.arcgisonline.com/ArcGIS/rest/services/' + 'Specialty/ESRI_StateCityHighway_USA/MapServer'},
            legend_title='ESRI USA Highway',
            legend_extent=[-173, 17, -65, 72]
        )

        # Define base map options
        esri_layer_names = [
            'NatGeo_World_Map',
            'Ocean_Basemap',
            'USA_Topo_Maps',
            'World_Imagery',
            'World_Physical_Map',
            'World_Shaded_Relief',
            'World_Street_Map',
            'World_Terrain_Base',
            'World_Topo_Map',
        ]
        esri_layers = [{'ESRI': {'layer': l}} for l in esri_layer_names]
        basemaps = [
            'Stamen',
            {'Stamen': {'layer': 'toner', 'control_label': 'Black and White'}},
            {'Stamen': {'layer': 'watercolor'}},
            'OpenStreetMap',
            'CartoDB',
            {'CartoDB': {'style': 'dark'}},
            {'CartoDB': {'style': 'light', 'labels': False, 'control_label': 'CartoDB-light-no-labels'}},
            {'XYZ': {'url': 'https://maps.wikimedia.org/osm-intl/{z}/{x}/{y}.png', 'control_label': 'Wikimedia'}}
            'ESRI',
        ]
        basemaps.extend(esri_layers)

        # Specify OpenLayers version
        MapView.ol_version = '5.3.0'

        # Define map view options
        map_view_options = MapView(
                height='600px',
                width='100%',
                controls=['ZoomSlider', 'Rotate', 'FullScreen',
                          {'MousePosition': {'projection': 'EPSG:4326'}},
                          {'ZoomToExtent': {'projection': 'EPSG:4326', 'extent': [-130, 22, -65, 54]}}],
                layers=[geojson_layer, geojson_point_layer, geoserver_layer, kml_layer, arc_gis_layer],
                view=view_options,
                basemap=basemaps,
                draw=drawing_options,
                legend=True
        )

        context = {'map_view_options': map_view_options}

    Template Example

    ::

        {% load tethys_gizmos %}

        {% gizmo map_view_options %}

    """  # noqa: E501
    gizmo_name = "map_view"
    ol_version = '5.3.0'
    cdn = 'https://cdn.jsdelivr.net/npm/openlayers@{version}/dist/ol{debug}.{ext}'
    alternate_cdn = 'https://cdnjs.cloudflare.com/ajax/libs/openlayers/{version}/ol{debug}.{ext}'
    local_url = 'tethys_gizmos/vendor/openlayers/{version}/ol.{ext}'

    def __init__(self, height='100%', width='100%', basemap=None, view={'center': [-100, 40], 'zoom': 2},
                 controls=[], layers=[], draw=None, legend=False, attributes={}, classes='', disable_basemap=False,
                 feature_selection=None):
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
        self.disable_basemap = disable_basemap
        self.feature_selection = feature_selection

    @classmethod
    def static_url(cls):
        return cls.cdn if cls.ol_version != '5.3.0' else cls.local_url

    @classmethod
    def debug(cls):
        # Note: Since version 5 OpenLayers now uses source maps instead of a '-debug' version of the code
        return '-debug' if settings.DEBUG and int(cls.ol_version[0]) < 5 else ''

    @classmethod
    def get_vendor_js(cls):
        """
        JavaScript vendor libraries to be placed in the
        {% block global_scripts %} block
        """
        openlayers_library = cls.static_url().format(
            version=cls.ol_version,
            debug=cls.debug(),
            ext='js'
        )

        return openlayers_library,

    @staticmethod
    def get_gizmo_js():
        """
        JavaScript specific to gizmo to be placed in the
        {% block scripts %} block
        """
        return ('tethys_gizmos/js/gizmo_utilities.js',
                'tethys_gizmos/js/tethys_map_view.js')

    @classmethod
    def get_vendor_css(cls):
        """
        CSS vendor libraries to be placed in the
        {% block styles %} block
        """
        openlayers_css = cls.static_url().format(
            version=cls.ol_version,
            debug=cls.debug(),
            ext='css'
        )

        return openlayers_css,

    @staticmethod
    def get_gizmo_css():
        """
        CSS specific to gizmo to be placed in the
        {% block content_dependent_styles %} block
        """
        return 'tethys_gizmos/css/tethys_map_view.min.css',


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

    """  # noqa: E501

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
        controls(list, required): List of drawing controls to add to the map. Valid options are 'Modify', 'Delete', 'Move', 'Point', 'LineString', 'Polygon' and 'Box'.
        initial(str, required): Drawing control to be enabled initially. Must be included in the controls list.
        output_format(str): Format to output to the hidden text area. Either 'WKT' (for Well Known Text format) or 'GeoJSON'. Defaults to 'GeoJSON'
        line_color(str): User control for customizing the stroke color of annotation objects
        fill_color(str): User control for customizing the fill color of polygons (suggest rgba format for setting transparency)
        point_color(str): User control for customizing the color of points

    Example

    ::

        drawing_options = MVDraw(
            controls=['Modify', 'Delete', 'Move', 'Point', 'LineString', 'Polygon', 'Box'],
            initial='Point',
            output_format='GeoJSON',
            line_color='#663399',
            fill_color='rgba(255,255,255,0.2)',
            point_color='#663399'
        )

    """  # noqa: E501

    def __init__(self, controls, initial, output_format='GeoJSON',
                 line_color="#ffcc33", fill_color='rgba(255, 255, 255, 0.2)',
                 point_color="#ffcc33"):
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
        self.fill_color = fill_color
        self.line_color = line_color
        self.point_color = point_color


class MVLayer(SecondaryGizmoOptions):
    """
    MVLayer objects are used to define map layers for the Map View Gizmo.

    Attributes:
        source (str, required): The source or data type of the layer (e.g.: ImageWMS)
        options (dict, required): A dictionary representation of the OpenLayers options object for ol.source.
        legend_title (str, required): The human readable name of the layer that will be displayed in the legend.
        layer_options (dict): A dictionary representation of the OpenLayers options object for ol.layer.
        editable (bool): If true the layer will be editable with the tethys_map_view drawing/editing tools.
        feature_selection (bool): Set to True to enable feature selection on this layer. Defaults to False.
        geometry_attribute (str): The name of the attribute in the shapefile that describes the geometry
        legend_classes (list): A list of MVLegendClass objects.
        legend_extent (list): A list of four ordinates representing the extent that will be used on "zoom to layer": [minx, miny, maxx, maxy].
        legend_extent_projection (str): The EPSG projection of the extent coordinates. Defaults to "EPSG:4326".
        tethys_data (dict): Dictionary representation of layer data

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

        # Define GeoServer Tile Layer with Custom tile grid
        # The default EPSG:900913 gridset can be used with OpenLayers.
        # You must ensure that OpenLayers requests tiles with the same gridset and origin as the gridset GeoServer uses
        # to use GeoWebCaching capabilities. This is done by setting the TILESORIGIN parameter and specifying a custom tileGrid.
        # Refer to OpenLayers API for ol.tilegrid.TileGrid for explanation and options.
        # See: http://docs.geoserver.org/2.7.0/user/webadmin/tilecache/index.html
        geoserver_layer = MVLayer(source='TileWMS',
                                  options={'url': 'http://192.168.59.103:8181/geoserver/wms',
                                           'params': {'LAYERS': 'topp:states',
                                                      'TILED': True,
                                                      'TILESORIGIN': '0.0,0.0'},
                                           'serverType': 'geoserver',
                                           'tileGrid': {
                                           'resolutions': [
                                               156543.03390625,
                                               78271.516953125,
                                               39135.7584765625,
                                               19567.87923828125,
                                               9783.939619140625,
                                               4891.9698095703125,
                                               2445.9849047851562,
                                               1222.9924523925781,
                                               611.4962261962891,
                                               305.74811309814453,
                                               152.87405654907226,
                                               76.43702827453613,
                                               38.218514137268066,
                                               19.109257068634033,
                                               9.554628534317017,
                                               4.777314267158508,
                                               2.388657133579254,
                                               1.194328566789627,
                                               0.5971642833948135,
                                               0.2985821416974068,
                                               0.1492910708487034,
                                               0.0746455354243517,
                                             ],
                                             'extent': [-20037508.34, -20037508.34, 20037508.34, 20037508.34],
                                             'origin': [0, 0],
                                             'tileSize': [256, 256]
                                           }
                                  },
                                  legend_title='USA Population')

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
    """  # noqa: E501

    def __init__(self, source, options, legend_title, layer_options=None, editable=True,
                 legend_classes=None, legend_extent=None,
                 legend_extent_projection='EPSG:4326',
                 feature_selection=False, geometry_attribute=None, data=None):
        """
        Constructor
        """
        super(MVLayer, self).__init__()

        self.source = source
        self.legend_title = legend_title
        self.options = options
        self.editable = editable
        self.layer_options = layer_options
        self.legend_classes = legend_classes
        self.legend_extent = legend_extent
        self.legend_extent_projection = legend_extent_projection
        self.feature_selection = feature_selection
        self.geometry_attribute = geometry_attribute
        self.data = data or dict()

        if feature_selection and not geometry_attribute:
            log.warning("geometry_attribute not defined -using default value 'the_geom'")


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

    """  # noqa: E501

    def __init__(self, type, value, fill='', stroke='', ramp=[]):
        """
        Constructor
        """

        # Initialize super class
        super(MVLegendClass, self).__init__()

        self.LEGEND_TYPE = 'mvlegend'
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


class MVLegendImageClass(SecondaryGizmoOptions):
    """
    MVLegendImageClasses are used to define the classes listed in the legend using a pre-generated image.

    Attributes:
        value (str, required): The value or name of the legend class.
        image_url (str, required): The url to the legend image.

    Example

    ::

        image_class = MVLegendImageClass(value='Cities',
                                         image_url='https://upload.wikimedia.org/wikipedia/commons/d/da/The_City_London.jpg'
                                         )
    """  # noqa: E501

    def __init__(self, value, image_url):
        """
        Constructor
        """
        # Initialize super class
        super(MVLegendImageClass, self).__init__()

        self.LEGEND_TYPE = 'mvlegendimage'
        self.value = value
        self.image_url = image_url


class MVLegendGeoServerImageClass(MVLegendImageClass):
    """
    MVLegendGeoServerImageClasses are used to define the classes listed in the legend using the GeoServer generated legend.

    Attributes:
        value (str, required): The value or name of the legend class.
        geoserver_url (str, required): The url to your geoserver (e.g. http://localhost:8181/geoserver).
        style (str, required): The name of the geoserver style (e.g. green).
        layer (str, required): The name of the geoserver layer (e.g. rivers).
        width (int): The legend width (default is 20).
        height (int): The legend height (default is 10).

    Example

    ::

        image_class = MVLegendGeoServerImageClass(value='Cities',
                                                  geoserver_url='http://localhost:8181/geoserver',
                                                  style='green',
                                                  layer='rivers',
                                                  width=20,
                                                  height=10)
    """  # noqa: E501

    def __init__(self, value, geoserver_url, style, layer, width=20, height=10):
        """
        Constructor
        """
        image_url = "{0}/wms?REQUEST=GetLegendGraphic&VERSION=1.0.0&" \
                    "STYLE={1}&FORMAT=image/png&WIDTH={2}&HEIGHT={3}&" \
                    "LEGEND_OPTIONS=forceRule:true&" \
                    "LAYER={4}".format(geoserver_url, style, width, height, layer)

        # Initialize super class
        super(MVLegendGeoServerImageClass, self).__init__(value, image_url)
