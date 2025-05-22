import logging
from tethys_portal.dependencies import vendor_static_dependencies
from .base import TethysGizmoOptions, SecondaryGizmoOptions

log = logging.getLogger("tethys.tethys_gizmos.gizmo_options.cesium_map_view")


class CesiumMapView(TethysGizmoOptions):
    """
    The Cesium Map View gizmo can be used to produce interactive maps of spatial data. It is powered by CesiumJS

    Shapes that are drawn on the map by users can be retrieved from the map via a hidden text field named 'geometry' and it is updated every time the map is changed. If the Cesium Map View is embedded in a form, the geometry that is drawn on the map will automatically be submitted with the rest of the form via the hidden text field.

    Attributes:
        cesium_ion_token(str): Cesium Ion Access Token. See: `Cesium Rest API - Authentication <https://cesium.com/learn/ion/ion-upload-rest/>`_.
        options(dict): Viewer basic options. One item in dictionary per option.
        globe(dict): Options to set on the Globe of the view.
        view(dict): Set the initial view of the map using various methods(e.g.: flyTo, setView).
        layers(list): Add one or more imagery layers to the map.
        entities(list):: Add one or more entities to the map.
        primitives(list): Add one or more primitives to the map.
        terrain(dict): Add terrain provider to the map.
        models(list): Add one or more 3D models to the map.
        clock(dict): Define custom clock options for viewer.
        height(str): Height of the map element. Any valid css unit of length (e.g.: '500px'). Defaults to '100%'.
        width(str): Width of the map element. Any valid css unit of length (e.g.: '100%'). Defaults to '100%'.
        draw(boolean): Turn drawing tools on/off.
        attributes(dict): A dictionary representing additional HTML attributes to add to the primary element (e.g. {"onclick": "run_me();"}).
        classes(str): Additional classes to add to the primary HTML element (e.g. "example-class another-class").

    **Cesium Version**

    You can specify the version of Cesium that you'd like to use by setting the ``cesium_version`` class property prior to creating your Cesium map view:

    ::

        CesiumMapView.cesium_version = "1.63.1"
        my_cesium_view = CesiumMapView(...)

    Or you can choose to use the latest release by setting the version to the empty string:

    ::

        CesiumMapView.cesium_version = ""
        my_cesium_view = CesiumMapView(...)

    **Cesium Ion Token**

    This is your Cesium Ion Access token that grants you access to the Cesium REST APIs. In newer version of Cesium this token is required for proper functioning of the map viewer. To learn how to obtain a token, see `Cesium REST API - Authentication <https://cesium.com/learn/ion/ion-upload-rest/>`_.

    ::

        cesium_access_token='mYf8k3t0KEn--asdfsdf98as7uj34n5a8-yvzhnj23q098-zdvnkj'

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

    Pass the following Globe options to ``CesiumMapView``:

    ::

        # Tethys CesiumMapView example
        cesium_map_view = CesiumMapView(
            globe={
                'enableLighting': True,
                'depthTestAgainstTerrain': True
            }
        )

    **View**

    Here is how the view option is defined using the Cesium JavaScript API (`Sandcastle - Camera <https://sandcastle.cesium.com/?src=Camera.html>`_):

    ::

        viewer.camera.flyTo({
            destination : Cesium.Cartesian3.fromDegrees(-122.22, 46.12, 5000.0),
            orientation : {
                 heading : Cesium.Math.toRadians(20.0),
                 pitch : Cesium.Math.toRadians(-35.0),
                 roll : 0.0
            }
        });

    In Tethys ``CesiumMapView``, you can define this setting using python as follows

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

    ``CesiumMapView`` supports all the imagery layers in the CesiumJS API (see `Imagery Providers <https://cesium.com/learn/cesiumjs-learn/cesiumjs-imagery/#more-imagery-providers>`_). It also support ``ImageWMS`` and ``TileWMS`` ``MVLayers`` (see: :ref:`gizmo_mvlayer`).
    You can load one or more imagery layers using the following pattern:

    ::

        layers=[
            {<layer_name>: {
                'imageryProvider': {<imagery_provider_class>: {
                    <option1>: <value1>,
                    <option2>: <value2>
                }
            },
            <MVLayer Object>
        ]

    Examples:

    * Bing: The following values can be used for mapStyle: Aerial, AerialWithLabels, CanvasDark, CanvasGray, CanvasLight, CollinsBart, OrdnanceSurvey, Road

    ::

        layers=[
            {'Bing Map': {
                'imageryProvider': {'Cesium.BingMapsImageryProvider': {
                    'url': 'https://dev.virtualearth.net',
                    'key': 'YouR-api-KEy',
                    'mapStyle': 'Aerial',
                }}
            }}
        ]

    * ESRI:

    ::

        layers=[
            {'Esri Arc GIS Map Server': {
                'imageryProvider': {'Cesium.ArcGisMapServerImageryProvider': [{
                    'url': 'https://services.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer'
                }]}
            }}
        ]

    * OpenStreetMap:

    ::

        layers=[
            {'Open Street Map': {
                'imageryProvider': {'Cesium.OpenStreetMapImageryProvider': {
                    'url': 'https://a.tile.openstreetmap.org/'
                }}
            }}
        ]

    * WMS Imagery Service:

    ::

        layers=[
            {'WMS Imagery Provider': {
                'imageryProvider': {'Cesium.WebMapServiceImageryProvider': [{
                    'url': 'https://sampleserver1.arcgisonline.com/ArcGIS/services/Specialty/ESRI_StatesCitiesRivers_USA/MapServer/WMSServer',
                    'layers': '0',
                    'proxy': {'Cesium.DefaultProxy': ['/proxy/']}
                }]}
            }}
        ]

    * Mix with MVLayer Objects

    ::

        layers=[
            {'Open Street Map': {
                'imageryProvider': {'Cesium.OpenStreetMapImageryProvider': {
                    'url': 'https://a.tile.openstreetmap.org/'
                }}
            }},
            MVLayer(
                source='ImageWMS',
                legend_title='MVLayer ImageWMS',
                options={
                    'url': 'https://demo.geo-solutions.it/geoserver/wms',
                    'params': {'LAYERS': 'topp:states'},
                    'serverType': 'geoserver'
                },
            )
        ]

    * More examples can be found at `Sandcastle - Imagery Layers Manipulation <https://sandcastle.cesium.com/?src=Imagery%20Layers%20Manipulation.html>`_

    **Entities**

    Supports CZML and GeoJSON entities. Also supports ``GeoJSON`` ``MVLayers`` (see: :ref:`gizmo_mvlayer`).

    * CZML Example:

    ::

        entities=[
            {
                'source': 'czml',
                'options': [
                    {
                        "id": "document",
                        "name": "CZML Geometries: Polygon",
                        "version": "1.0"
                    },
                    {
                        "id": "whitePolygon",
                        "name": "White polygon on surface",
                        "polygon": {"positions": {
                            "cartographicDegrees": [
                                -115.0, 37.0, 0,
                                -115.0, 32.0, 0,
                                -107.0, 33.0, 0,
                                -102.0, 31.0, 0,
                                -102.0, 35.0, 0
                            ]
                        }},
                        "material": {
                            "solidColor": {
                                "color": {
                                    "rgba": [255, 0, 0, 255]
                                }
                            }
                        }
                    }
                ]
            }
        ]

    * GeoJSON Example:

    ::

        entities=[
            {
                'source': 'geojson',
                'options': {
                    'type': 'FeatureCollection',
                    'crs': {
                        'type': 'name',
                        'properties': {
                            'name': 'EPSG:4326'
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
                                'coordinates': [[35.9326113, -17.6789142], [71.8652227, 17.6789142]]
                            }
                        },
                        {
                            'type': 'Feature',
                            'geometry': {
                                'type': 'Polygon',
                                'coordinates': [
                                    [[-44.9157642, -8.9465739], [-35.9326114, 8.9465739], [-26.9494585, -8.9465739]]
                                ]
                            }
                        }
                    ]
                }
            }
        ]

    * GeoJSON MVLayer

    ::

        entities=[
            MVLayer(
                source='GeoJSON',
                legend_title='MVLayer GeoJSON Example',
                options={
                    'type': 'FeatureCollection',
                    'crs': {
                        'type': 'name',
                        'properties': {
                            'name': 'EPSG:4326'
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
                                'coordinates': [[35.9326113, -17.6789142], [71.8652227, 17.6789142]]
                            }
                        },
                        {
                            'type': 'Feature',
                            'geometry': {
                                'type': 'Polygon',
                                'coordinates': [
                                    [[-44.9157642, -8.9465739], [-35.9326114, 8.9465739], [-26.9494585, -8.9465739]]
                                ]
                            }
                        }
                    ]
                }
            )
        ]

    **Primitives**

    Support Cesium Primitive such as Cesium Ion

    You can load a Cessium Ion using the following pattern:

    ::

        primitives=[
            {'Cesium_Ion_Data': {'Cesium.Cesium3DTileset': {'url': {'Cesium.IonResource.fromAssetId': 123}}}},
            MVLayer(
                source='CesiumPrimitive',
                legend_title='Cesium 3D Buildings',
                options={'Cesium.Cesium3DTileset': {'url': {'Cesium.IonResource.fromAssetId': 96188}}},
                data={'layer_name': 'Cesium_Buildings', 'layer_variable': 'variable', 'layer_id': 1}
            )
        ]

    **Terrain**

    Supports all the terrain providers available in Cesium (see `Cesium Terrain Providers <https://cesium.com/learn/cesiumjs-learn/cesiumjs-terrain/#terrain-providers>`_

    You can load a terrain provider using the following pattern:

    ::

        terrain={
            'terrainProvider': {<terrain_provider_class>: {
                <option1>: <value1>,
                <option2>: <value2>
            }
        }

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

        models=[
            {'Cesium_Airplane': {
                'model': {
                    'uri': object1,
                    'show': True,
                    'minimumPixelSize': 128,
                    'maximumScale': 20000,
                    'shadows': 'enabled',
                },
                'name': 'Cesium Airplane',
                'orientation': {
                    'Cesium.Transforms.headingPitchRollQuaternion': [
                        {'Cesium.Cartesian3.fromDegrees': [-123.0744619, 44.0503706, 5000]},
                        {'Cesium.HeadingPitchRoll': [{'Cesium.Math.toRadians': 135}, 0, 0]}
                ]},
                'position': {'Cesium.Cartesian3.fromDegrees': [-123.0744619, 44.0503706, 5000]},
            }},
            MVLayer(
                source='CesiumModel',
                legend_title='Cesium Ballon',
                options={'model': {
                    'uri': object2,
                    'show': True,
                    'minimumPixelSize': 128,
                    'maximumScale': 20000,
                    'shadows': 'enabled'},
                    'name': 'Cesium_Ballon',
                    'orientation': {
                        'Cesium.Transforms.headingPitchRollQuaternion':
                            [{'Cesium.Cartesian3.fromDegrees': [-123.0744619, 44.0503706, 5000]},
                             {'Cesium.HeadingPitchRoll': [{'Cesium.Math.toRadians': 135}, 0, 0]}]},
                    'position': {'Cesium.Cartesian3.fromDegrees': [-123.0744619, 44.0503706, 5000]}
                 },
                data={
                    'layer_id': "cesium_ballon_id",
                    'layer_name': "Cesium_Ballon",
                    'popup_title': "Cesium Ballon",
                }
            ),
        ]

    **Cesium Ion Resource using Assest ID**

    Support loading data from Cesium Ion assets and resources.

    For example:

    ::

        primitives = [{'Cesium_World_Terrain': {'Cesium.Cesium3DTileset': {'url': {'Cesium.IonResource.fromAssetId': 1}}}},
                      MVLayer(source='CesiumPrimitive', legend_title='Cesium 3D Buildings',
                              options={'Cesium.Cesium3DTileset': {'url': {'Cesium.IonResource.fromAssetId': 96188}}},
                              data={'layer_name': 'Cesium_Buildings', 'layer_variable': 'variable', 'layer_id': 1})]

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

    Pass the following Clock options to ``CesiumMapView``:

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

    You can find a lots of way to define cesium attributes in the sandcastle page: `Sandcastle <https://sandcastle.cesium.com/>`_

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
    cesium_version = vendor_static_dependencies["cesiumjs"].version

    def __init__(
        self,
        options=None,
        globe=None,
        view=None,
        layers=None,
        entities=None,
        primitives=None,
        terrain=None,
        models=None,
        clock=None,
        height="100%",
        width="100%",
        draw=False,
        attributes=None,
        classes="",
        cesium_ion_token="",
    ):
        """
        Constructor
        """
        # Initialize super class
        super(CesiumMapView, self).__init__(attributes=attributes, classes=classes)
        self.height = height
        self.width = width
        self.options = options or {}
        self.globe = globe or {}
        self.clock = clock or {}
        self.view = view or {}
        self.layers = layers or []
        self.entities = entities or []
        self.primitives = primitives or []
        self.terrain = terrain or {}
        self.models = models or []
        self.draw = draw
        self.cesium_ion_token = cesium_ion_token

    @classmethod
    def get_vendor_js(cls):
        """
        JavaScript vendor libraries to be placed in the
        {% block global_scripts %} block
        """
        return (
            vendor_static_dependencies["cesiumjs"].get_custom_version_url(
                url_type="js", version=cls.cesium_version
            ),
        )

    @staticmethod
    def get_gizmo_js():
        """
        JavaScript specific to gizmo to be placed in the
        {% block scripts %} block
        """
        return (
            "tethys_gizmos/js/gizmo_utilities.js",
            "tethys_gizmos/js/cesium_map_view.js",
            "tethys_gizmos/js/DrawHelper.min.js",
        )

    @classmethod
    def get_vendor_css(cls):
        """
        CSS vendor libraries to be placed in the
        {% block styles %} block
        """
        return (
            vendor_static_dependencies["cesiumjs"].get_custom_version_url(
                url_type="css", version=cls.cesium_version
            ),
        )

    @staticmethod
    def get_gizmo_css():
        """
        CSS specific to gizmo to be placed in the
        {% block content_dependent_styles %} block
        """
        return (
            "tethys_gizmos/css/cesium_map_view.min.css",
            "tethys_gizmos/css/DrawHelper.min.css",
        )


class CMVEntity(SecondaryGizmoOptions):
    """
    CMVEntity objects are used to define map layers for the Map View Gizmo.

    Attributes:
        options (dict, required): A dictionary representation of the OpenLayers options object for ol.source.
        layer_options (dict): A dictionary representation of the OpenLayers options object for ol.layer.
        editable (bool): If true the layer will be editable with the tethys_map_view drawing/editing tools.
        data (dict): Dictionary representation of layer data

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

        geojson_layer = CMVLayer(source='GeoJSON',
                                options=geojson_object,
                                layer_options={'style_map': style_map},
                                )
    """  # noqa: E501

    def __init__(
        self,
        source,
        document,
        legend_title,
        layer_options=None,
        editable=False,
        data=None,
    ):
        """
        Constructor
        """
        super().__init__()

        self.source = source
        self.document = document
        self.legend_title = legend_title
        self.editable = editable
        self.layer_options = layer_options
        self.data = data or dict()
