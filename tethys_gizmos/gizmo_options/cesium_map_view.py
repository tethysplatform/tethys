from .base import TethysGizmoOptions
import logging
log = logging.getLogger('tethys.tethys_gizmos.gizmo_options.cesium_map_view')


class CesiumMapView(TethysGizmoOptions):
    """
        The Cesium Map View gizmo can be used to produce interactive maps of spatial data. It is powered by CesiumJS

        Shapes that are drawn on the map by users can be retrieved from the map via a hidden text field named 'geometry' and it is updated every time the map is changed. If the Cesium Map View is embedded in a form, the geometry that is drawn on the map will automatically be submitted with the rest of the form via the hidden text field.

        Attributes:
            height(str): Height of the map element. Any valid css unit of length (e.g.: '500px'). Defaults to '100%'.
            width(str): Width of the map element. Any valid css unit of length (e.g.: '100%'). Defaults to '100%'.
            options(dict): Viewer basic options. One item in dictionary per option.
            globe(dict): Options to set on the Globe of the view.
            view(dict): Set the initial view of the map using various methods(e.g.: flyTo, setView)
            layers(dict): Add imagery layer to map. One item in dictionary per imagery layer.
            entities(dict):: Add entities to map. One item in dictionary per entity
            terrain(dict): Add terrain provider to the map.
            models(dict): Add 3D model to map. One item in dictionary per model.
            clock(dict): Define custom clock options for viewer.
            draw(boolean): Turn drawing tools on/off.
            attributes(dict): A dictionary representing additional HTML attributes to add to the primary element (e.g. {"onclick": "run_me();"}).
            classes(str): Additional classes to add to the primary HTML element (e.g. "example-class another-class").



        **Cesium Version**

        You can specify the version of Cesium that you'd like to use by setting the ``cesium_version`` class property prior to creating your Cesium map view:

        ::

            CesiumMapView.cesium_version = "1.51"
            my_cesium_view = CesiumMapView(...)

        Or you can choose to use the latest release by setting the version to the empty string:

        ::

            CesiumMapView.cesium_version = ""
            my_cesium_view = CesiumMapView(...)

        **Options**

        Basic options for cesium example:

            ::

                options={'shouldAnimate': False, 'timeline': False, 'homeButton': False}
        **Globe**
        You can specify options that are often set on the Globe object associated with the Cesium viewer. For example, to achieve the equivalent of these calls in the Cesiumm JavaScript API:
        ::
            // Cesium JS Example
            viewer.scene.globe.enableLighting = true;
            viewer.scene.globe.depthTestAgainstTerrain = true;
        Pass the following Globe options to CesiumMapView:
        ::
            # Tethys CesiumMapView example
            cesium_map_view = CesiumMapView(
                globe={
                    'enableLighting': True,
                    'depthTestAgainstTerrain': True
                }
            )

        **View**

        Here is how the view option is defined using the Cesium JavaScript API (https://cesiumjs.org/Cesium/Build/Apps/Sandcastle/index.html?src=Camera.html):

            ::

                viewer.camera.flyTo({
                    destination : Cesium.Cartesian3.fromDegrees(-122.22, 46.12, 5000.0),
                    orientation : {
                         heading : Cesium.Math.toRadians(20.0),
                         pitch : Cesium.Math.toRadians(-35.0),
                         roll : 0.0
                    }
                });

        In Tethys CesiumMapView, you can define this setting using python as follows

            ::

                view={'flyTo': {
                    'destination': {'Cesium.Cartesian3.fromDegrees': [-122.19, 46.25, 5000.0]},
                    'orientation': {
                         'heading': {'Cesium.Math.toRadians': [20]},
                         'pitch': {'Cesium.Math.toRadians': [-35]},
                         'roll': 0.0,
                    }
                }}

        **Layers**

        CesiumMapView supports all the imagery layers in cesiumjs: https://cesiumjs.org/tutorials/Imagery-Layers-Tutorial/#imagery-providers
        You can load a imagery layers using the following pattern:

            ::

                layers={'Type of Imagery Layers (for your reference only)': {'imageryProvider': 'method/class to load the provider'}

        Examples:

        * Bing: The following values can be used for mapStyle: Aerial, AerialWithLabels, CanvasDark, CanvasGray, CanvasLight, CollinsBart, OrdnanceSurvey, Road

            ::

                layers={'BingMap': {
                    'imageryProvider': {'Cesium.BingMapsImageryProvider': {
                        'url': 'https://dev.virtualearth.net',
                        'key': 'YouR-api-KEy',
                        'mapStyle': 'Aerial',
                    }}
                }}

        * ESRI:

            ::

                layers={'EsriArcGISMapServer': {
                    'imageryProvider': {'Cesium.ArcGisMapServerImageryProvider': [{
                        'url': 'https://services.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer'
                    }]}
                }}

        * OpenStreetMap:

            ::

                layers={'OpenStreetMap': {
                    'imageryProvider': {'Cesium.createOpenStreetMapImageryProvider':[]}
                }}

        * MapQuest OpenStreetMap:

            ::

                layers={'MapQuestOpenStreetMap': {
                    'imageryProvider': {Cesium.createOpenStreetMapImageryProvider: [{
                        'url' : 'https://otile1-s.mqcdn.com/tiles/1.0.0/osm/'
                    }]}
                }}

        * More examples can be found at https://cesiumjs.org/Cesium/Build/Apps/Sandcastle/index.html?src=Imagery%20Layers%20Manipulation.html

        **Entities**

        Support most entities in Cesium: https://cesiumjs.org/tutorials/Visualizing-Spatial-Data/#shapes-and-volumes

        Example loading a czml:

            ::

                entities={'czml': [
                    {
                        "id": "document",
                        "name": "CZML Geometries: Polygon",
                        "version": "1.0"
                    },
                    {
                        "id": "redPolygon",
                        "name": "Red polygon on surface",
                        "polygon": {"positions": {
                            "cartographicDegrees": [
                                -115.0, 37.0, 0,
                                -115.0, 32.0, 0,
                                -107.0, 33.0, 0,
                                -102.0, 31.0, 0,
                                -102.0, 35.0, 0
                            ]
                        },
                        "material": {
                            "solidColor": {
                                "color": {
                                    "rgba": [255, 0, 0, 255]
                                }
                            }
                        }
                    }
                ]}

        **Terrain**

        Support all the terrain provider available in Cesium: https://cesiumjs.org/tutorials/Terrain-Tutorial/#terrain-providers

        You can load a terrain provider using the following pattern:

        ::

            terrain={'terrainProvider': 'method/class and args to load the provider'}

        For example:

        ::

            terrain={'terrainProvider': {
                'Cesium.createWorldTerrain': {
                    'requestVertexNormals' : True,
                    'requestWaterMask': True
                }
            }}

        **Models**

        Support loading glTF 3d model. It could be traditional glTF with a .gltf extension or binary glTF with a .glb extension

        For example:

        ::

            object = 'link_to.glb'

            models={'Cesium_Airplane': {
                'model': {
                    'uri': object1,
                    'show': True,
                    'minimumPixelSize': 128,
                    'maximumScale': 20000,
                    'shadows': 'enabled',
                },
                'name': object,
                'orientation': {
                    'Cesium.Transforms.headingPitchRollQuaternion': [
                        {'Cesium.Cartesian3.fromDegrees': [-123.0744619, 44.0503706, 5000]},
                        {'Cesium.HeadingPitchRoll': [{'Cesium.Math.toRadians' : 135}, 0, 0]}
                    ]
                },
                'position': {'Cesium.Cartesian3.fromDegrees': [-123.0744619, 44.0503706, 5000]},
            }}
        **Clock**
        You can customize the clock on the viewer such as specifying the starting date and time and specifying the time step interval. For example, to achieve the equivalent of these calls in the Cesiumm JavaScript API:
        ::
            // Cesium JS Example
            var clock = new Cesium.Clock({
                startTime : Cesium.JulianDate.fromIso8601('2017-07-11T00:00:00Z'),
                stopTime : Cesium.JulianDate.fromIso8601('2017-07-11T24:00:00Z'),
                currentTime : Cesium.JulianDate.fromIso8601('2017-07-11T10:00:00Z'),
                clockRange : Cesium.ClockRange.LOOP_STOP,
                clockStep : Cesium.ClockStep.SYSTEM_CLOCK_MULTIPLIER,
                multiplier : 1000,
                shouldAnimate : true
            });
            var viewer = new Cesium.Viewer('cesiumContainer', {
                clockViewModel : new Cesium.ClockViewModel(clock),
            });
        Pass the following Clock options to CesiumMapView:
        ::
            # Tethys CesiumMapView example
            cesium_map_view = CesiumMapView(
                clock = {'clock': {'Cesium.Clock': {
                    'startTime': {'Cesium.JulianDate.fromIso8601': ['2017-07-11T00:00:00Z']},
                    'stopTime': {'Cesium.JulianDate.fromIso8601': ['2017-07-11T24:00:00Z']},
                    'currentTime': {'Cesium.JulianDate.fromIso8601': ['2017-07-11T10:00:00Z']},
                    'clockRange': 'Cesium.ClockRange.LOOP_STOP',
                    'clockStep': 'Cesium.ClockStep.SYSTEM_CLOCK_MULTIPLIER',
                    'multiplier': 1000,
                    'shouldAnimate': True
                }}}
            )

        **Drawing**

        The following drawing options are supported:

        * Add marker
        * 2D polyline
        * 2D polygon
        * Extent
        * Circle

        All the drawing options can be view in the log and are available upon submit using a hidden text field named 'geometry'

        The drawing feature also have the following tools:

        * Delete All: Use to delete all the drawing features on the map.
        * Turn logging on or off: Use to turn on or off logging.

        **Translate Cesium Attributes from Javascript to Python**

        You can find a lots of way to define cesium attributes in the sandcastle page: https://cesiumjs.org/Cesium/Build/Apps/Sandcastle/index.html

        Here are a few things to remember:

        1. Put Cesium method/class in a dictionary with the method/class as key and its argument in a list.
        2. If the argument of a given Cesium method/class has another Cesium method/class as its argument, simply follows the same procedure in 1.

        For example:

        ::

            'orientation': {'Cesium.Transforms.headingPitchRollQuaternion': [
                {'Cesium.Cartesian3.fromDegrees': [-123.0744619, 44.0503706, 5000]},
                {'Cesium.HeadingPitchRoll': [{'Cesium.Math.toRadians' : 135}, 0, 0]}
            ]}
    """  # noqa: E501
    gizmo_name = "cesium_map_view"

    # Set Cesium Default Release Version.
    cesium_version = ""

    def __init__(self, options={}, globe={}, view={}, layers={}, entities={}, terrain={}, models={}, clock={},
                 height='100%', width='100%', draw=False, attributes={}, classes=''):
        """
        Constructor
        """
        # Initialize super class
        super(CesiumMapView, self).__init__(attributes=attributes, classes=classes)
        self.height = height
        self.width = width
        self.options = options
        self.globe = globe
        self.clock = clock
        self.view = view
        self.layers = layers
        self.entities = entities
        self.terrain = terrain
        self.models = models
        self.draw = draw

    @classmethod
    def get_vendor_js(cls):
        """
        JavaScript vendor libraries to be placed in the
        {% block global_scripts %} block
        """
        # To use build version, cesium_version is blank. Otherwise, it will use the specified release version.
        if cls.cesium_version:
            cesium_js = 'https://cesiumjs.org/releases/' + cls.cesium_version + '/Build/Cesium/Cesium.js'
        else:
            cesium_js = 'https://cesiumjs.org/Cesium/Build/Cesium/Cesium.js'
        return (cesium_js,)

    @staticmethod
    def get_gizmo_js():
        """
        JavaScript specific to gizmo to be placed in the
        {% block scripts %} block
        """
        return ('tethys_gizmos/js/gizmo_utilities.js',
                'tethys_gizmos/js/cesium_map_view.js',
                'tethys_gizmos/js/DrawHelper.min.js')

    @classmethod
    def get_vendor_css(cls):
        """
        CSS vendor libraries to be placed in the
        {% block styles %} block
        """
        if cls.cesium_version:
            cesium_css = 'https://cesiumjs.org/releases/' + cls.cesium_version + '/Build/Cesium/Widgets/widgets.css'
        else:
            cesium_css = 'https://cesiumjs.org/Cesium/Build/Cesium/Widgets/widgets.css'
        return (cesium_css,)

    @staticmethod
    def get_gizmo_css():
        """
        CSS specific to gizmo to be placed in the
        {% block content_dependent_styles %} block
        """
        return ('tethys_gizmos/css/cesium_map_view.min.css',
                'tethys_gizmos/css/DrawHelper.min.css')
