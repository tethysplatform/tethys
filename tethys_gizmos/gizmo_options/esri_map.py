from .base import TethysGizmoOptions, SecondaryGizmoOptions

__all__ = ['ESRIMap','EMView','EMLayer']

class ESRIMap(TethysGizmoOptions):
    """
    ESRI Map View

    The ESRI Map View is similar to Map View, but it is powered by ArcGIS API for JavaScript 4.0

    Attributes
        height(string, required): Height of map container in normal css units
        width(string, required): Width of map container in normal css units
        basemap(string, required): Basemap layer. Values=[streets,satellite,hybrid,topo,gray,dark-gray,oceans,national-geographic,terrain,osm,dark-gray-vector,gray-vector,street-vector,topo-vector,streets-night-vector,streets-relief-vector,streets-navigation-vector]
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

        {% gizmo esri_map_view esri_map_view_options %}

    """

    def __init__(self, height='100%', width='100%', basemap='topo',view={'center':[-100,40],'zoom':2},layers=[]):
        """
        Constructor
        """
        # Initialize super class
        super(ESRIMap, self).__init__()

        self.height = height
        self.width = width
        self.basemap = basemap
        self.view = view
        self.layers = layers

class EMView(SecondaryGizmoOptions):
    """
       EMView objects are used to define the initial view of the ESRI Map View. The initial view is set by specifying a center and a zoom level.

       Attributes:
           projection(str): Projection of the center coordinates given. This projection will be used to transform the coordinates into the default map projection (EPSG:3857).
           center(list): An array with the coordinates of the center point of the initial view.
           zoom(int or float): The zoom level for the initial view.
           maxZoom(int or float): The maximum zoom level allowed. Defaults to 28.
           minZoom(int or float): The minimum zoom level allowed. Defaults to 0.

       Example

       ::

           view_options = EMView(
               center=[-100, 40],
               zoom=3.5,
           )

       """
    def __init__(self, center, zoom):
        """
        Constructor
        """
        # Initialize super class
        super(EMView, self).__init__()

        self.center = center
        self.zoom = zoom


class EMLayer(SecondaryGizmoOptions):

    def __init__(self,type,url):
        """
        Constructor
        """
        #Initialize super class
        super(EMLayer,self).__init__()
        self.type = type
        self.url = url

