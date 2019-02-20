from .base import TethysGizmoOptions, SecondaryGizmoOptions

__all__ = ['ESRIMap', 'EMView', 'EMLayer']


class ESRIMap(TethysGizmoOptions):
    """
    ESRI Map View

    The ESRI Map View is similar to Map View, but it is powered by ArcGIS API for JavaScript 4.0

    Attributes
        height(string, required): Height of map container in normal css units
        width(string, required): Width of map container in normal css units
        basemap(string, required): Basemap layer. Values=[streets,satellite,hybrid,topo,gray,dark-gray,oceans, national-geographic,terrain,osm,dark-gray-vector,gray-vector,street-vector, topo-vector,streets-night-vector,streets-relief-vector,streets-navigation-vector]
        zoom(string,required): Zoom Level of the Basemap.
        view(EMView): An EVView object specifying the initial view or extent for the map

    Example

    ::

        # CONTROLLER
        from tethys_sdk.gizmos import ESRIMapView

        esri_map_view_options = {'height': '700px',
                                   'width': '100%',
                                   'basemap':'topo'}

        # TEMPLATE

        {% gizmo esri_map_view_options %}

    """  # noqa: E501
    gizmo_name = "esri_map"

    def __init__(self, height='100%', width='100%', basemap='topo', view={'center': [-100, 40], 'zoom': 2}, layers=[]):
        """
        Constructor
        """
        # Initialize super class
        super().__init__()

        self.height = height
        self.width = width
        self.basemap = basemap
        self.view = view
        self.layers = layers

    @staticmethod
    def get_vendor_js():
        """
        Javascript vendor libraries to be placed in the
        {% block global_scripts %} block
        """
        esri_javascript_library = 'https://js.arcgis.com/4.2/'
        return (esri_javascript_library,)

    @staticmethod
    def get_gizmo_js():
        """
        JavaScript specific to gizmo to be placed in the
        {% block scripts %} block
        """
        return ('tethys_gizmos/js/esri_map.js',)

    @staticmethod
    def get_vendor_css():
        """
        CSS vendor libraries to be placed in the
        {% block styles %} block
        """
        return ('https://js.arcgis.com/4.2/esri/css/main.css',)


class EMView(SecondaryGizmoOptions):
    """
       EMView objects are used to define the initial view of the ESRI Map View. The initial view is set by specifying a center and a zoom level.

       Attributes:
           center(list): An array with the coordinates of the center point of the initial view.
           zoom(int or float): The zoom level for the initial view.

       Example

       ::

           view_options = EMView(
               center=[-100, 40],
               zoom=3.5,
           )

       """  # noqa: E501
    def __init__(self, center, zoom):
        """
        Constructor
        """
        # Initialize super class
        super().__init__()

        self.center = center
        self.zoom = zoom


class EMLayer(SecondaryGizmoOptions):
    """
    EMLayer objects are used to define map layers for the ESRI Map Gizmo.

    Attributes:
        type (str,required): The ESRI Layer Type (e.g.: FeatureLayer, ImageLayer)
        url (str,required): The ESRI Layer WMS url

    Example

    ::

    #Define ArcGIS FeatureLayer

    esri_feature_layer = EMLayer(type='FeatureLayer', url='http://geoserver.byu.edu/arcgis/rest/services/Alabama_Flood/Flood_45/MapServer/0')

    #Define ArcGIS ImageLayer

    esri_image_layer = EMLayer(type='ImageryLayer', url='https://sampleserver6.arcgisonline.com/arcgis/rest/services/NLCDLandCover2001/ImageServer')

    """  # noqa: E501
    def __init__(self, type, url):
        """
        Constructor
        """
        # Initialize super class
        super().__init__()
        self.type = type
        self.url = url
