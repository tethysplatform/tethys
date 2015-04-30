from .base import TethysGizmoOptions, SecondaryGizmoOptions

__all__ = ['MapViewOptions', 'MapViewDrawOptions', 'MapViewViewOptions', 'MapViewLayer', 'MapViewVectorLegendItem']


class MapViewOptions(TethysGizmoOptions):
    """
    The Map View gizmo can be used to visualize maps of spatial data. Map View is powered by OpenLayers 3, an open source pure javascript mapping library.

    Attributes:
        height(str): Height of the map element. Any valid css unit of length (e.g.: '500px'). Defaults to '520px'.
        width(str): Width of the map element. Any valid css unit of length (e.g.: '100%'). Defaults to '100%'.
        basemap(str or dict): The base map to show on the map which can be either OpenStreetMap, MapQuest, or a Bing map. Valid values for the string option are: 'OpenStreetMap' and 'MapQuest'. If you wish to configure the base map with options, you must use the dictionary form. The dictionary form is required to use a Bing map, because an API key must be passed as an option. See details below.
        view(MapViewViewOptions): The initial view or extent for the map.
        controls(list): A list of controls to add to the map. The list can be a list of strings or a list of dictionaries. Valid strings are 'ZoomSlider', 'Rotate', 'FullScreen', 'ScaleLine', 'ZoomToExtent', and 'MousePosition'.
        layers(list): A list of layer dictionaries where the singular key of each dictionary specifies the type of layer and the value is another dictionary with the options for that layer. Supported layer types are 'WMS', 'TiledWMS', 'GeoJSON', and 'KML'. See notes below details.
        draw(MapViewDrawOptions): A MapViewDrawOptions object.

    Example

    ::

        # CONTROLLER

        from tethys_gizmos.gizmo_options import MapView, MapViewDrawOptions, MapViewViewOptions

        view_options = MapViewViewOptions(
            projection='EPSG:4326',
            center=[-100, 40],
            zoom=3.5,
            maxZoom=18,
            minZoom=3
        )

        drawing_options = MapViewDrawOptions(
            controls=['Modify', 'Move', 'Point', 'LineString', 'Polygon', 'Box'],
            initial='Point',
            output_format='WKT'
        )

        map_view_options = MapViewOptions(
            height='500px',
            width='100%',
            controls=['ZoomSlider',
                     'Rotate',
                     'FullScreen',
                     {'MousePosition': {'projection': 'EPSG:4326'}}],
            layers=[{'WMS': {'url': 'http://demo.opengeo.org/geoserver/wms',
                            'params': {'LAYERS': 'topp:states'},
                            'serverType': 'geoserver'}}],
            view=view_options,
            basemap='OpenStreetMap',
            draw=drawing_options,
            legend=False
        )

        # TEMPLATE

        {% gizmo map_view map_view_options %}

    """

    def __init__(self, height='100%', width='100%', basemap='OpenStreetMap', view={'center': [-100, 40], 'zoom': 2},
                 controls=[], layers=[], draw=None, legend=False):
        """
        Constructor
        """
        # Initialize super class
        super(MapViewOptions, self).__init__()

        self.height = height
        self.width = width
        self.basemap = basemap
        self.view = view
        self.controls = controls
        self.layers = layers
        self.draw = draw
        self.legend = legend


class MapViewViewOptions(SecondaryGizmoOptions):
    """
    MapViewViewOptions objects are used to define the initial view of the Map View. The initial view is set by specifying a center and a zoom level.

    Attributes:
        projection(str): Projection of the center coordinates given. This projection will be used to transform the coordinates into the default map projection (EPSG:3857).
        center(list): An array with the coordinates of the center point of the initial view.
        zoom(int or float): The zoom level for the initial view.
        maxZoom(int or float): The maximum zoom level allowed. Defaults to 28.
        minZoom(int or float): The minimum zoom level allowed. Defaults to 0.

    Example

    ::

        view_options = MapViewViewOptions(
            projection='EPSG:4326',
            center=[-100, 40],
            zoom=3.5,
            maxZoom=18,
            minZoom=3
        )
    """

    def __init__(self, projection, center, zoom, maxZoom=28, minZoom=0):
        """
        Constructor
        """
        # Initialize super class
        super(MapViewViewOptions, self).__init__()

        self.projection = projection
        self.center = center
        self.zoom = zoom
        self.maxZoom = maxZoom
        self.minZoom = minZoom


class MapViewDrawOptions(SecondaryGizmoOptions):
    """
    MapViewDrawOptions objects are used to define the drawing options for Map View.

    Attributes:
        controls(list, required): List of drawing controls to add to the map. Valid options are 'Modify', 'Move', 'Point', 'LineString', 'Polygon' and 'Box'.
        initial(str, required): Drawing control to be enabled initially. Must be included in the controls list.
        output_format(str): Format to output to the hidden text area. Either 'WKT' (for Well Known Text format) or 'GeoJSON'. Defaults to 'GeoJSON'

    Example

    ::

        drawing_options = MapViewDrawOptions(
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
        super(MapViewDrawOptions, self).__init__()

        self.controls = controls

        # Validate initial
        if initial not in self.controls:
            raise ValueError('Va'
                             'lue of "initial" must be contained in the "controls" list.')
        self.initial = initial
        self.output_format = output_format


class MapViewRasterLegendItem(SecondaryGizmoOptions):
    """
    MapViewLegendItems are used to specify the legend representation of a feature.

    Attributes:
        min (float): Min value of ramp range.
        max (float): Max value of ramp range.
        ramp (MapViewColorRamp): A MapViewColorRamp object
    """

    def __init__(self):
        """
        Constructor
        """
        # Initialize super class
        super(MapViewRasterLegendItem, self).__init__()


class MapViewVectorLegendItem(SecondaryGizmoOptions):
    """
    MapViewLegendItems are used to specify the legend representation of a feature.

    Attributes:
        type (str): The type of feature to be represented. Either 'point', 'line', or 'polygon'.
        value (str): The value or name of the legend item.
        color (str): The hex rgb color of the feature (e.g.: '#00ff00').

    Example

    ::

        point_item = MapViewVectorLegendItem(type='point', value='Cities', color='#00ff00')

    """

    def __init__(self):
        """
        Constructor
        """
        # Initialize super class
        super(MapViewVectorLegendItem, self).__init__()


class MapViewLayer(SecondaryGizmoOptions):
    """
    MapViewLayer objects are used to define map layers in the Map View Gizmo

    Attributes:
        source (str): The source or data type of the layer (e.g.: ImageWMS)
        title (str): The human readable name of the layer.
        openlayers_object (dict): A dictionary representation of the OpenLayers layer options object.
        legend (tuple): A tuple or list of MapViewLegendItems.
    """

    def __init__(self, source, title, openlayers_object, legend=None):
        """
        Constructor
        """
        super(MapViewLayer, self).__init__()

        self.source = source
        self.title = title
        self.openlayers_object = openlayers_object
        self.legend = legend


class MapViewWmsLayer(MapViewLayer):
    """
    MapViewWmsLayer objects are used to define Web Mapping Service (WMS) layers for the Map View Gizmo

    Attributes:
        title (str): The human readable name of the layer.
        wms_url (str): URL of the WMS server
        params (dict): Parameters of the WMS call. The LAYERS parameter
        server_type (str): The type of the WMS server (e.g.: 'geoserver')
    """

    def __init__(self, title, wms_url, params, server_type, legend=None):
        """
        Constructor
        """
        # Construct the open layers object
        openlayers_object = {'url': wms_url,
                             'params': params,
                             'serverType': server_type}

        super(MapViewWmsLayer, self).__init__(source='WMS', title=title, openlayers_object=openlayers_object,
                                              legend=legend)