"""
********************************************************************************
* Name: map_layout.py
* Author: nswain
* Created On: June 24, 2021
* Copyright: (c) Aquaveo 2021
********************************************************************************
"""
from abc import ABCMeta, abstractmethod
import collections
import copy
from io import BytesIO
import json
import logging
import os
import requests
import uuid
from zipfile import ZipFile

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
import shapefile  # PyShp

from tethys_gizmos.gizmo_options import SlideSheet
from tethys_layouts.utilities import classproperty
from tethys_layouts.views.tethys_layout import TethysLayout
from tethys_sdk.permissions import has_permission, permission_required
from tethys_sdk.gizmos import ToggleSwitch, CesiumMapView, MapView, MVLayer, MVView

log = logging.getLogger(f'tethys.{__name__}')

_COLOR_RAMPS = {
    "Default": ["#fff100", "#ff8c00", "#e81123", "#ec008c", "#68217a", "#00188f", "#00bcf2", "#00b294", "#009e49",
                "#bad80a"],
    "Blue": ["#f7fbff", "#deebf7", "#c6dbef", "#9ecae1", "#6baed6", "#4292c6", "#2171b5", "#08519c", "#083582",
             "#022259"],
    "Blue and Red": ["#a50026", "#d73027", "#f46d43", "#fdae61", "#fee090", "#e0f3f8", "#abd9e9", "#74add1", "#4575b4",
                     "#313695"],
    "Elevated": ["#96D257", "#278C39", "#2A7B45", "#829C41", "#DBB82E", "#AE4818", "#842511", "#61370F", "#806346",
                 "#C2C2C2", "#FFFFFF"],
    "Flower Field": ["#e60049", "#0bb4ff", "#50e991", "#e6d800", "#9b19f5", "#ffa300", "#dc0ab4", "#b3d4ff",
                     "#00bfa0", "#f0cccc"],
    "Galaxy Berries": ["#0040bf", "#a3cc52", "#b9a087", "#a01fcc", "#5bb698", "#5e851e", "#d1943f",
                       "#96aedc", "#629ed9", "#8a64b3"],
    "Heat Map": ["#90a1be", "#a761aa", "#af4980", "#b83055", "#c80000", "#d33300", "#de6600", "#e99900", "#f4cc00",
                 "#ffff00"],
    "Olive Harmony": ["#437a75", "#d9d78c", "#bf7860", "#72231f", "#afbfa2", "#5a9bc8", "#89a6a6", "#99905c",
                      "#414b8c", "#a664a0"],
    "Mother Earth": ["#a03500", "#d9b400", "#3264c8", "#72b38e", "#986ba1", "#b9a087", "#4c91bf", "#a5d236",
                     "#96aedc", "#ad8516"],
    "Rainbow": ["#fff100", "#ff8c00", "#e81123", "#ec008c", "#68217a", "#00188f", "#00bcf2", "#00b294", "#009e49",
                "#bad80a"],
    "Rainforest Frogs": ["#dc4b00", "#3c6ccc", "#d9dc00", "#91d900", "#986ba1", "#d99f00", "#4db478",
                         "#4cafdc", "#96aedc", "#d7a799"],
    "Retro FLow": ["#007fd9", "#443dbf", "#881fc5", "#bf00bf", "#d43f70", "#d9874c", "#b6a135", "#adbf27",
                   "#c4dc66", "#ebe498"],
    "Sunset Fade": ["#b30000", "#7c1158", "#4421af", "#1a53ff", "#0d88e6", "#00b7c7", "#5ad45a", "#8be04e",
                    "#c5d96d", "#ebdc78"],
}

_DEFAULT_TILE_GRID = {
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
        0.0373227677121758,
        0.0186613838560879,
        0.009330691928044,
        0.004665345964022,
        0.002332672982011,
        0.0011663364910055,
        0.0005831682455027,
        0.0002915841227514,
        0.0001457920613757
    ],
    'extent': [-20037508.34, -20037508.34, 20037508.34, 20037508.34],
    'origin': [0.0, 0.0],
    'tileSize': [256, 256]
}


class MapLayout(TethysLayout):
    """
    Controller for the MapLayout view. Pass kwargs matching property names to as_controller()
        to override their values and configure the MapLayout view.

    Recommended Properties:
        app (TethysApp): The class of the app contained in app.py.
        base_template (str): Template to use as base template. Recommend overriding this to be your app's base template. Defaults to "tethys_layouts/tethys_layout.html".
        map_subtitle (str): The subtitle to display on the MapLayout view.
        map_title (str): The title to display on the MapLayout view.

    Optional Properties:
        back_url (str): URL that will be added to the back button. No back button if not provided.
        cesium_ion_token (str): Cesium Ion API token. Required if map_type is "cesium_map_view". See: https://cesium.com/learn/cesiumjs-learn/cesiumjs-quickstart/
        default_center (2-list<float>): Coordinates of the initial center for the map. Defaults to [-98.583, 39.833].
        default_disable_basemap (bool) Set to True to disable the basemap.
        default_zoom (int): Default zoom level. Defaults to 4.
        geocode_api_key = An Open Cage Geocoding API key. Required to enable address search/geocoding feature. See: https://opencagedata.com/api#quickstart
        geoserver_workspace = Name of the GeoServer workspace of layers if applicable. Defaults to None.
        initial_map_extent = The initial zoom extent for the map. Defaults to [-180, -90, 180, 90].
        feature_selection_multiselect (bool): Set to True to enable multi-selection when feature selection is enabled. Defaults to False.
        feature_selection_sensitivity (int): Feature selection sensitivity/relative search radius. Defaults to 4.
        layer_tab_name (str) Name of the "Layers" tab. Defaults to "Layers".
        map_type (str): Type of map gizmo to use. One of "tethys_map_view" or "cesium_map_view". Defaults to "tethys_map_view".
        max_zoom (int): Maximum zoom level. Defaults to 28.
        min_zoom (int): Minimum zoom level. Defaults to 0.
        properties_popup_enabled (bool): Set to False to disable the properties popup. Defaults to True.
        sds_setting_name (str): Name of a Spatial Dataset Service Setting in the app to pass to MapManager when initializing. The SDS will be retrieved as an engine and passed to the constructor of the MapManager using the kwarg "sds_engine".
        show_custom_layer (bool): Show the "Custom Layers" item in the Layers tree when True. Users can add WMS layers to the Custom Layers layer group dynamically. Defaults to True.
        show_legends (bool): Show the Legend tab. Defaults to False.
    """  # noqa: E501
    __metaclass__ = ABCMeta

    # Changing these will likely break the MapLayout
    template_name = 'tethys_layouts/map_layout/map_layout.html'
    http_method_names = ['get', 'post']
    _geocode_endpoint = 'http://api.opencagedata.com/geocode/v1/geojson'
    _default_popup_excluded_properties = ['id', 'type', 'layer_name']

    # Required Properties
    map_subtitle = ''  # TODO: just use layout_title and layout_subtitle?
    map_title = ''

    # Optional Properties
    cesium_ion_token = None
    default_center = [-98.583, 39.833]
    default_disable_basemap = False
    default_zoom = 4
    geocode_api_key = None
    geoserver_workspace = ''
    initial_map_extent = [-180, -90, 180, 90]
    feature_selection_mutiselect = False
    feature_selection_sensitivity = 4
    layer_tab_name = 'Layers'
    map_type = 'tethys_map_view'
    max_zoom = 28
    min_zoom = 0
    properties_popup_enabled = True
    sds_setting_name = ''
    show_custom_layer = True
    show_legends = False

    COLOR_RAMPS = copy.deepcopy(_COLOR_RAMPS)
    DEFAULT_TILE_GRID = _DEFAULT_TILE_GRID

    @classproperty
    def map_extent(cls):
        if not getattr(cls, '_map_extent', None):
            view, extent = cls._get_map_extent_and_view()
            cls._map_extent = extent
            cls._default_view = view
        return cls._map_extent

    @classproperty
    def default_view(cls):
        if not getattr(cls, '_default_view', None):
            view, extent = cls._get_map_extent_and_view()
            cls._map_extent = extent
            cls._default_view = view
        return cls._default_view

    @classproperty
    def sds_engine(cls):
        if not cls.sds_setting_name:
            return None
        if not getattr(cls, '_sds_engine', None):
            cls._sds_engine = cls.app.get_spatial_dataset_engine_setting(cls.sds_setting_name)
        return cls._sds_engine

    # Abstract Methods -------------------------------------------------- #
    @abstractmethod
    def compose_map(self, request, *args, **kwargs):
        """
        Compose the MapView object.
        Args:
            request(HttpRequest): A Django request object.

        Returns:
            MapView, 4-list<float>, list<LayerGroupDicts>: The MapView, extent, and list of LayerGroup dictionaries.
        """
        raise NotImplemented('You must extend MapLayout and implement the compose_map method.')

    # Hooks ------------------------------------------------------------- #
    @classmethod
    def get_initial_map_extent(cls):
        """
        Get the initial extent for the map.

        Returns:
            4-list<float>: The initial extent [minx, miny, maxx, maxy].
        """
        return cls.initial_map_extent

    def get_plot_for_layer_feature(self, layer_name, feature_id):
        """
        Retrieves plot data for given feature on given layer.

        Args:
            layer_name(str): Name/id of layer.
            feature_id(str): PostGIS Feature ID of feature.

        Returns:
            str, list<dict>, dict: plot title, data series, and layout options, respectively.
        """
        layout = {
            'xaxis': {
                'title': layer_name
            },
            'yaxis': {
                'title': 'Undefined'
            }
        }

        data = [{
            'name': feature_id,
            'mode': 'lines',
            'x': [1, 2, 3, 4],
            'y': [10, 15, 13, 17],
        }]
        return 'Undefined', data, layout

    @classmethod
    def get_vector_style_map(cls):
        """
        Builds the style map for vector layers.

        Returns:
            dict: the style map.
        """
        color = 'gold'
        style_map = {
            'Point': {'ol.style.Style': {
                'image': {'ol.style.Circle': {
                    'radius': 5,
                    'fill': {'ol.style.Fill': {
                        'color': color,
                    }},
                    'stroke': {'ol.style.Stroke': {
                        'color': color,
                    }}
                }}
            }},
            'LineString': {'ol.style.Style': {
                'stroke': {'ol.style.Stroke': {
                    'color': color,
                    'width': 2
                }}
            }},
            'Polygon': {'ol.style.Style': {
                'stroke': {'ol.style.Stroke': {
                    'color': color,
                    'width': 2
                }},
                'fill': {'ol.style.Fill': {
                    'color': 'rgba(255, 215, 0, 0.1)'
                }}
            }},
        }

        return style_map

    def should_disable_basemap(self, request, *args, **kwargs):
        """
        Hook to override disabling the basemap.

        Args:
            request (HttpRequest): The request.

        Returns:
            bool: True to disable the basemap.
        """
        return self.default_disable_basemap

    # TethysLayout Method Implementations ----------------------------------- #
    def get_context(self, request, context, *args, **kwargs):
        """
        Create context for the Map Layout view.

        Args:
            request (HttpRequest): The request.
            context (dict): The context dictionary.

        Returns:
            dict: modified context dictionary.
        """  # noqa: E501
        # Compose the Map
        # TODO: refactor to create map_view and pass to compose_map - get_map_layers?
        map_view, map_extent, layer_groups = self.compose_map(
            request=request,
            *args, **kwargs
        )

        map_view = self._build_map_view(request, layer_groups, map_extent, *args, **kwargs)

        # Prepare context
        context.update({
            'enable_properties_popup': self.properties_popup_enabled,
            'geocode_enabled': self.geocode_api_key is not None,
            'layer_groups': layer_groups,
            'layer_tab_name': self.layer_tab_name,
            'map_extent': map_extent,
            'map_type': self.map_type,
            'map_view': map_view,
            'nav_subtitle': self.map_subtitle,
            'nav_title': self.map_title,
            'show_custom_layer': self.show_custom_layer,
            'show_legends': self.show_legends,
            'workspace': self.geoserver_workspace,
        })

        if context.get('show_public_toggle', False):
            layer_dropdown_toggle = ToggleSwitch(display_text='',
                                                 name='layer-dropdown-toggle',
                                                 on_label='Yes',
                                                 off_label='No',
                                                 on_style='success',
                                                 off_style='danger',
                                                 initial=True,
                                                 size='small',
                                                 classes='layer-dropdown-toggle')
            context.update({'layer_dropdown_toggle': layer_dropdown_toggle})

        # Add plot slide sheet
        plot_slidesheet = SlideSheet(
            id='plot-slide-sheet',
            title='Plot',
            content_template='tethys_layouts/map_layout/map_plot.html'
        )

        context.update({'plot_slide_sheet': plot_slidesheet})

        return context

    def get_permissions(self, request, permissions, *args, **kwargs):
        """
        Perform permissions checks for MapLayout specific features.

        Args:
            request (HttpRequest): The request.
            permissions (dict): The permissions dictionary with boolean values.

        Returns:
            dict: modified permissions dictionary.
        """
        permissions = {
            'can_download': has_permission(request, 'can_download'),
            'can_use_geocode': has_permission(request, 'use_map_geocode'),
            'can_use_plot': has_permission(request, 'use_map_plot'),
            'show_public_toggle': has_permission(request, 'toggle_public_layers'),
            'show_remove': has_permission(request, 'remove_layers'),
            'show_rename': has_permission(request, 'rename_layers'),
        }
        return permissions

    # Private View Helpers -------------------------------------------------- #
    def _build_map_view(self, request, map_view, layer_groups, map_extent, *args, **kwargs):
        """
        TODO: Refactor to create the MapView and return it.
        """
        # Reset/override map settings for common baseline
        map_view.legend = False  # Ensure the built-in legend is not turned on.
        map_view.height = '100%'  # Ensure 100% height
        map_view.width = '100%'  # Ensure 100% width
        map_view.controls = [
            'Rotate',
            'FullScreen',
            {'ZoomToExtent': {
                'projection': 'EPSG:4326',
                'extent': map_extent
            }}
        ]
        # Configure initial basemap visibility
        map_view.disable_basemap = self.should_disable_basemap(
            request=request,
            *args, **kwargs
        )
        # Configure feature selection
        map_view.feature_selection = {
            'multiselect': self.feature_selection_mutiselect,
            'sensitivity': self.feature_selection_sensitivity,
        }

        # Check if we need to create a blank custom layer group
        create_custom_layer = True
        for layer_group in layer_groups:
            if layer_group['id'] == 'custom_layers':
                create_custom_layer = False
                break

        # Create the Custom Layers layer group
        if create_custom_layer:
            custom_layers = self.build_layer_group(
                id="custom_layers",
                display_name="Custom Layers",
                layers=[],
                layer_control='checkbox',
                visible=True
            )
            layer_groups.append(custom_layers)

        # Override MapView with CesiumMapView if Cesium is the chosen map_type.
        if self.map_type == "cesium_map_view":
            map_view = self._build_ceisum_map_view(map_view)

        return map_view

    @classmethod
    def _build_mv_layer(cls, layer_source, layer_name, layer_title, layer_variable, options, layer_id=None,
                        extent=None, visible=True, public=True, selectable=False, plottable=False, has_action=False,
                        excluded_properties=None, popup_title=None, geometry_attribute=None, style_map=None,
                        show_download=False, times=None):
        """
        Build an MVLayer object with supplied arguments.
        Args:
            layer_source(str): OpenLayers Source to use for the MVLayer (e.g.: "TileWMS", "ImageWMS", "GeoJSON").
            layer_name(str): Name of GeoServer layer (e.g.: agwa:3a84ff62-aaaa-bbbb-cccc-1a2b3c4d5a6b7c8d-model_boundaries).
            layer_title(str): Title of MVLayer (e.g.: Model Boundaries).
            layer_variable(str): Variable type of the layer (e.g.: model_boundaries).
            layer_id(UUID, int, str): layer_id for non geoserver layer where layer_name may not be unique.
            visible(bool): Layer is visible when True. Defaults to True.
            selectable(bool): Enable feature selection. Defaults to False.
            plottable(bool): Enable "Plot" button on pop-up properties. Defaults to False.
            has_action(bool): Enable "Action" button on pop-up properties. Defaults to False.
            extent(list): Extent for the layer. Optional.
            popup_title(str): Title to display on feature popups. Defaults to layer title.
            excluded_properties(list): List of properties to exclude from feature popups.
            geometry_attribute(str): Name of the geometry attribute. Optional.
            style_map(dict): Style map dictionary. See MVLayer documentation for examples of style maps. Optional.
            show_download(boolean): enable download layer. (only works for geojson layer).
            times (list): List of time steps if layer is time-enabled. Times should be represented as strings in ISO 8601 format (e.g.: ["20210322T112511Z", "20210322T122511Z", "20210322T132511Z"]). Currently only supported in CesiumMapView.
        Returns:
            MVLayer: the MVLayer object.
        """  # noqa: E501

        # Derive popup_title if not given
        if not popup_title:
            popup_title = layer_title

        data = {
            'layer_id': str(layer_id) if layer_id else layer_name,
            'layer_name': layer_name,
            'popup_title': popup_title,
            'layer_variable': layer_variable,
            'toggle_status': public,
        }

        # Process excluded properties
        properties_to_exclude = copy.deepcopy(cls._default_popup_excluded_properties)

        if plottable:
            properties_to_exclude.append('plot')

        if excluded_properties and isinstance(excluded_properties, (list, tuple)):
            for ep in excluded_properties:
                if ep not in properties_to_exclude:
                    properties_to_exclude.append(ep)

        data.update({'excluded_properties': properties_to_exclude})

        if plottable:
            data.update({'plottable': plottable})

        if has_action:
            data.update({'has_action': has_action})

        if not extent:
            extent = cls.map_extent

        # Build layer options
        layer_options = {"visible": visible, "show_download": show_download}

        if style_map:
            layer_options.update({'style_map': style_map})

        mv_layer = MVLayer(
            source=layer_source,
            options=options,
            layer_options=layer_options,
            legend_title=layer_title,
            legend_extent=extent,
            legend_classes=[],
            data=data,
            feature_selection=selectable,
            times=times,
        )

        if geometry_attribute:
            mv_layer.geometry_attribute = geometry_attribute

        return mv_layer

    def _build_ceisum_map_view(self, map_view):
        """
        Translate the layers of the given MapView into Cesium Layers and Entities and build CesiumMapView.

        Args:
            map_view (MapView): A MapView Gizmo object.

        Returns:
            CesiumMapView: A CesiumMapView populated with translated layers.
        """
        if not self.cesium_ion_token:
            raise RuntimeError('You must set the "cesium_ion_token" attribute of the '
                               'MapLayout to use the Cesium "map_type".')

        # Translate the MapView.layers into Cesium layers and entities
        layers, entities = self._translate_layers_to_cesium(map_view.layers)

        # Build CesiumMapView
        CesiumMapView.cesium_version = "1.74"
        cesium_map_view = CesiumMapView(
            cesium_ion_token=self.cesium_ion_token,
            options={
                'contextOptions': {
                    'webgl': {
                        'xrCompatible': True,
                        'alpha': True,
                        'preserveDrawingBuffer': True,
                    }
                },
                'vrButton': False,
                'scene3DOnly': True,
            },
            terrain={
                'terrainProvider': {
                    'Cesium.createWorldTerrain': {
                        'requestVertexNormals': True,
                        'requestWaterMask': True
                    }
                }
            },
            layers=layers,
            entities=entities
        )
        return cesium_map_view

    @classmethod
    def _get_map_extent_and_view(cls):
        """
        Get the default view and extent for the project.

        Returns:
            MVView, 4-list<float>: default view and extent of the project.
        """
        extent = cls.get_initial_map_extent()

        # Compute center
        center = cls.default_center
        if extent and len(extent) >= 4:
            center_x = (extent[0] + extent[2]) / 2.0
            center_y = (extent[1] + extent[3]) / 2.0
            center = [center_x, center_y]

        # Construct the default view
        view = MVView(
            projection='EPSG:4326',
            center=center,
            zoom=cls.default_zoom,
            maxZoom=cls.max_zoom,
            minZoom=cls.min_zoom
        )

        return view, extent

    def _translate_layers_to_cesium(self, map_view_layers):
        """
        Map MVLayers to Cesium Layers (WMS) and Entities (vector).
            Only supports ImageWMS, TileWMS, and GeoJSON MVLayers.

        Args:
            map_view_layers (list<MVLayer>): A list of MVLayers.

        Returns:
            (list<MVLayer>, list<MVLayer>): Lists of layers and entities (entities, layers).
        """
        cesium_layers = []
        cesium_entities = []
        for layer in map_view_layers:
            if layer['source'] in ['ImageWMS', 'TileWMS']:
                cesium_layers.append(layer)
            elif layer['source'] in ['GeoJSON']:
                cesium_entities.append(layer)

        return cesium_layers, cesium_entities

    # AJAX Handlers --------------------------------------------------------- #
    def get_plot_data(self, request, *args, **kwargs):
        """
        Load plot from given parameters.

        Args:
            request (HttpRequest): The request.

        Returns:
            JsonResponse: title, data, and layout options for the plot.
        """
        # Get request parameters
        layer_name = request.POST.get('layer_name', '')
        feature_id = request.POST.get('feature_id', '')

        # Initialize MapManager
        title, data, layout = self.get_plot_for_layer_feature(layer_name, feature_id)

        return JsonResponse({'title': title, 'data': data, 'layout': layout})

    def save_custom_layers(self, request, *args, **kwargs):
        """
        An AJAX handler method that persists custom layers added to map by user.

        Args:
            request(HttpRequest): The request.

        Returns:
            JsonResponse: success.
        """
        # TODO: Implement a method that does not require the database. JSON File? Localstorage?
        display_name = request.POST.get('layer_name', '')
        layer_uuid = request.POST.get('uuid', '')
        service_link = request.POST.get('service_link', '')
        service_type = request.POST.get('service_type', 'WMS')
        service_layer_name = request.POST.get('service_layer_name', '')
        custom_layer = [{'layer_id': layer_uuid, 'display_name': display_name, 'service_link': service_link,
                         'service_type': service_type, 'service_layer_name': service_layer_name}]
        custom_layers = resource.get_attribute('custom_layers')
        if custom_layers is None:
            custom_layers = []
        custom_layers.extend(custom_layer)
        # TODO: Should use self._build_mv_layer or at the very least MVLayer
        resource.set_attribute('custom_layers', custom_layers)
        session.commit()
        return JsonResponse({'success': True})

    def remove_custom_layer(self, request, *args, **kwargs):
        """
        An AJAX handler method that removes persisted custom layers removed by user.
        Args:
            request(HttpRequest): The request.

        Returns:
            JsonResponse: success.
        """
        layer_id = request.POST.get('layer_id', '')
        layer_group_type = request.POST.get('layer_group_type', '')
        if layer_group_type == 'custom_layers':
            custom_layers = resource.get_attribute(layer_group_type)
            if custom_layers is not None:
                new_custom_layers = []
                for custom_layer in custom_layers:
                    if custom_layer['layer_id'] != layer_id:
                        new_custom_layers.append(custom_layer)
                # TODO: Implement a method that does not require the database. JSON File? Localstorage?
                resource.set_attribute(layer_group_type, new_custom_layers)
        session.commit()
        return JsonResponse({'success': True})

    def build_legend_item(self, request, *args, **kwargs):
        """
        A jQuery.load() handler method that renders the HTML for a legend.
        """
        # Get request parameters
        legend_div_id = json.loads(request.POST.get('div_id'))
        minimum = json.loads(request.POST.get('minimum'))
        maximum = json.loads(request.POST.get('maximum'))
        color_ramp = json.loads(request.POST.get('color_ramp'))
        prefix = json.loads(request.POST.get('prefix'))
        color_prefix = json.loads(request.POST.get('color_prefix'))
        first_division = json.loads(request.POST.get('first_division'))
        layer_id = json.loads(request.POST.get('layer_id'))

        legend = {
            'divisions': dict(),
        }

        divisions = self.generate_custom_color_ramp_divisions(
            min_value=minimum,
            max_value=maximum,
            color_ramp=color_ramp, prefix=prefix,
            color_prefix=color_prefix,
            first_division=first_division
        )

        division_string = self.build_param_string(**divisions)
        for label in divisions.keys():
            if color_prefix in label and int(label.replace(color_prefix, '')) >= first_division:
                legend['divisions'][float(divisions[label.replace(color_prefix, prefix)])] = divisions[label]

        legend['divisions'] = collections.OrderedDict(
            sorted(legend['divisions'].items())
        )

        r = render(
            request,
            'tethys_layouts/map_layout/color_ramp_component.html',
            {'legend': legend}
        )

        html_str = str(r.content, 'utf-8')
        response = JsonResponse({
            'success': True,
            'response': html_str,
            'div_id': legend_div_id,
            'color_ramp': color_ramp,
            'division_string': division_string,
            'layer_id': layer_id
        })
        return response

    def build_layer_group_tree_item(self, request, *args, **kwargs):
        """
        A jQuery.loads() handler that renders the HTML for a layer group tree item.

        status (create/append): create is create a whole new layer group with all the layer items associated with it
                                append is append an associated layer into an existing layer group
        """
        # Get request parameters
        status = request.POST.get('status', 'create')
        layer_group_name = request.POST.get('layer_group_name')
        layer_group_id = request.POST.get('layer_group_id')
        layer_names = json.loads(request.POST.get('layer_names'))
        layer_ids = json.loads(request.POST.get('layer_ids'))
        layer_legends = json.loads(request.POST.get('layer_legends'))
        show_rename = json.loads(request.POST.get('show_rename', 'true'))
        show_remove = json.loads(request.POST.get('show_remove', 'true'))
        show_download = json.loads(request.POST.get('show_download', 'false'))
        layers = []

        # Reconstruct the MVLayer objects
        for i in range(len(layer_names)):
            layers.append(self._build_mv_layer(
                layer_source="GeoJSON",
                layer_name=layer_ids[i],
                layer_title=layer_names[i],
                layer_variable=layer_legends[i],
                options=None,
            ))

        # Build Layer groups
        layer_group = self.build_layer_group(layer_group_id, layer_group_name, layers=layers)
        context = {
            'layer_group': layer_group,
            'show_rename': show_rename,
            'show_remove': show_remove,
            'show_download': show_download
        }

        if status == 'create':
            template = 'tethys_layouts/map_layout/layer_group_content.r'
        else:
            # Only works for one layer at a time for now.
            template = 'tethys_layouts/map_layout/layer_item_content.r'
            context['layer'] = layers[0]

        r = render(request, template, context)

        html_str = str(r.content, 'utf-8')
        return JsonResponse({'success': True, 'response': html_str})

    @permission_required('use_map_geocode', raise_exception=True)
    def find_location_by_query(self, request, *args, **kwargs):
        """"
        An AJAX handler that performs geocoding queries.

        Args:
            request(HttpRequest): The request.
        """
        if not self.geocode_api_key:
            raise RuntimeError('Can not run GeoCode query because no API token was supplied. Please provide the '
                               'API key via the "geocode_api_key" attribute of the MapLayoutView.')

        query = request.POST.get('q', None)
        extent = request.POST.get('extent', None)

        params = {
            'query': query,
            'key': self.geocode_api_key
        }

        if extent:
            params['bounds'] = extent

        response = requests.get(
            url=self._geocode_endpoint,
            params=params
        )

        if response.status_code != 200:
            json = {'success': False,
                    'error': response.text}
            return JsonResponse(json)

        # Construct friendly name for address select
        r_json = response.json()

        # Construct success json and parse out needed info
        json = {'success': True,
                'results': []}

        for address in r_json['features']:
            point = address['geometry']['coordinates']
            scale = 0.001

            if 'bounds' in address['properties']:
                bounds = address['properties']['bounds']

                minx = float(bounds['southwest']['lng'])
                maxx = float(bounds['northeast']['lng'])
                miny = float(bounds['southwest']['lat'])
                maxy = float(bounds['northeast']['lat'])

                diffx = maxx - minx

                if diffx < scale:
                    minx -= scale
                    miny -= scale
                    maxx += scale
                    maxy += scale

            else:
                minx = point[0] - scale
                maxx = point[0] + scale
                miny = point[1] - scale
                maxy = point[1] + scale

            bbox = [minx, miny, maxx, maxy]

            max_name_length = 40
            display_name = address['properties']['formatted']
            if len(display_name) > max_name_length:
                display_name = display_name[:max_name_length] + '...'

            geocode_id = uuid.uuid4()

            json['results'].append({
                'text': display_name,
                'point': point,
                'bbox': bbox,
                'id': 'geocode-' + str(geocode_id)
            })

        return JsonResponse(json)

    @permission_required('use_map_geocode', raise_exception=True)
    def find_location_by_advanced_query(self, request, *args, **kwargs):
        """"
        An AJAX handler that performs an advanced address search.

        Args:
            request(HttpRequest): The request.
        """
        if not self.geocode_api_key:
            raise RuntimeError('Can not run GeoCode query because no API token was supplied. Please provide the '
                               'API key via the "geocode_api_key" attribute of the MapLayoutView.')

        query = request.POST.get('q', None)
        # location = request.POST.get('l', None)

        params = {
            'query': query,
            'key': self.geocode_api_key
        }

        response = requests.get(
            url=self._geocode_endpoint,
            params=params
        )

        if response.status_code != 200:
            json = {'success': False,
                    'error': response.text}
            return JsonResponse(json)

        # Construct friendly name for address select
        r_json = response.json()

        # Construct success json and parse out needed info
        json = {'success': True,
                'results': []}

        for address in r_json['features']:
            point = address['geometry']['coordinates']
            scale = 0.001

            if 'bounds' in address['properties']:
                bounds = address['properties']['bounds']

                minx = float(bounds['southwest']['lng'])
                maxx = float(bounds['northeast']['lng'])
                miny = float(bounds['southwest']['lat'])
                maxy = float(bounds['northeast']['lat'])

                diffx = maxx - minx

                if diffx < scale:
                    minx -= scale
                    miny -= scale
                    maxx += scale
                    maxy += scale

            else:
                minx = point[0] - scale
                maxx = point[0] + scale
                miny = point[1] - scale
                maxy = point[1] + scale

            bbox = [minx, miny, maxx, maxy]

            max_name_length = 40
            display_name = address['properties']['formatted']
            if len(display_name) > max_name_length:
                display_name = display_name[:max_name_length] + '...'

            geocode_id = uuid.uuid4()

            json['results'].append({
                'text': display_name,
                'point': point,
                'bbox': bbox,
                'id': 'geocode-' + str(geocode_id)
            })

        return JsonResponse(json)

    def convert_geojson_to_shapefile(self, request, *args, **kwargs):
        """
        AJAX handler that converts GeoJSON data into a shapefile for download.
        credit to:
        https://github.com/TipsForGIS/geoJSONToShpFile/blob/master/geoJ.py
        Args:
            request(HttpRequest): The request.

        Returns:
            JsonResponse: success.
        """
        json_data = json.loads(request.POST.get('data', ''))
        layer_id = request.POST.get('id', '0')
        json_type = json_data['features'][0]['geometry']['type']

        if json_type == 'Polygon':
            shpfile_obj = shapefile.Writer(shapefile.POLYGON)
        elif json_type == 'Point':
            shpfile_obj = shapefile.Writer(shapefile.POINT)
        elif json_type == 'LineString':
            shpfile_obj = shapefile.Writer(shapefile.POLYLINE)
        else:
            raise ValueError('Only GeoJson of the following types are supported: Polygon, Point, or LineString')

        shpfile_obj.autoBalance = 1

        columns_list = json_data['features'][0]['properties'].keys()
        for i in columns_list:
            shpfile_obj.field(str(i), 'C', '50')

        geometries = list()
        attributes = list()
        for feature in json_data['features']:
            if feature['geometry']['type'] == json_type:
                geometries.append(feature['geometry']['coordinates'])
            attributes_per_feature = list()
            for attribute_feature in columns_list:
                attributes_per_feature.append(str(feature['properties'][str(attribute_feature)]))
            attributes.append(attributes_per_feature)

        for geo in geometries:
            if json_type == 'Polygon':
                shpfile_obj.poly(polys=geo)
            elif json_type == 'Point':
                shpfile_obj.point(geo[0], geo[1])
            elif json_type == 'LineString':
                shpfile_obj.line(lines=[geo])

        for attr in attributes:
            shpfile_obj.record(*attr)

        # write shapefile
        shp_file = layer_id + "_" + json_type
        prj_file = open(shp_file + '.prj', 'w')
        prj_str = 'GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],' \
                  'PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]]'
        prj_file.write(prj_str)
        prj_file.close()
        shpfile_obj.save(shp_file)

        in_memory = BytesIO()
        shp_file_ext = ['prj', 'shp', 'dbf', 'shx']

        with ZipFile(in_memory, "w") as my_zip:
            for ext in shp_file_ext:
                my_zip.write(shp_file + "." + ext)

        # Clean up
        for ext in shp_file_ext:
            if os.path.exists(shp_file + "." + ext):
                os.remove(shp_file + "." + ext)

        response = HttpResponse(content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename="' + shp_file + '.zip' + '"'

        in_memory.seek(0)
        response.write(in_memory.read())
        return response

    # Utilities ------------------------------------------------------------- #
    @classmethod
    def get_wms_endpoint(cls, public=True):
        """
        Get the public wms endpoint for GeoServer.
        """
        wms_endpoint = cls.sds_engine.public_endpoint if public else cls.sds_engine.endpoint
        wms_endpoint = wms_endpoint.replace('rest', 'wms')

        # Add trailing slash for consistency.
        if wms_endpoint[-1] != '/':
            wms_endpoint += '/'
        return wms_endpoint

    @classmethod
    def build_layer_group(cls, id, display_name, layers, layer_control='checkbox', visible=True, public=True):
        """
        Build a layer group object.

        Args:
            id(str): Unique identifier for the layer group.
            display_name(str): Name displayed in MapView layer selector/legend.
            layers(list<MVLayer>): List of layers to include in the layer group.
            layer_control(str): Type of control for layers. Either 'checkbox' or 'radio'. Defaults to checkbox.
            visible(bool): Whether layer group is initially visible. Defaults to True.
            public(bool): enable public to see this layer group if True.
        Returns:
            dict: Layer group definition.
        """
        if layer_control not in ['checkbox', 'radio']:
            raise ValueError('Invalid layer_control. Must be on of "checkbox" or "radio".')

        layer_group = {
            'id': id,
            'display_name': display_name,
            'control': layer_control,
            'layers': layers,
            'visible': visible,
            'toggle_status': public,
        }
        return layer_group

    @classmethod
    def build_param_string(cls, **kwargs):
        """
        Build a VIEWPARAMS or ENV string with given kwargs (e.g.: 'foo:1;bar:baz')

        Args:
            **kwargs: key-value pairs of paramaters.

        Returns:
            str: parameter string.
        """
        if not kwargs:
            return ''

        joined_pairs = []
        for k, v in kwargs.items():
            joined_pairs.append(':'.join([k, str(v)]))

        param_string = ';'.join(joined_pairs)
        return param_string

    @classmethod
    def build_legend(cls, layer, units=""):
        """
        Build Legend data for a given layer

        Args:
            layer: result.layer object
            units: unit for the legend.
        Returns:
            Legend data associate with the layer.
        """
        legend_info = ""
        if layer.get('color_ramp_division_kwargs') is not None:
            legend_key = layer['layer_variable']
            layer_id = layer['layer_id'] if layer['layer_id'] else layer['layer_name']
            if ":" in legend_key:
                legend_key = legend_key.replace(":", "_")

            div_kwargs = layer['color_ramp_division_kwargs']
            min_value = div_kwargs['min_value']
            max_value = div_kwargs['max_value']
            color_ramp = div_kwargs['color_ramp'] if 'color_ramp' in div_kwargs.keys() else 'Default'
            prefix = div_kwargs['prefix'] if 'prefix' in div_kwargs.keys() else 'val'
            color_prefix = div_kwargs['color_prefix'] if 'color_prefix' in div_kwargs.keys() else 'color'
            first_division = div_kwargs['first_division'] if 'first_division' in div_kwargs.keys() else 1

            legend_info = {
                'legend_id': legend_key,
                'title': layer['layer_title'].replace("_", " "),
                'divisions': dict(),
                'color_list': cls.COLOR_RAMPS.keys(),
                'layer_id': layer_id,
                'min_value': min_value,
                'max_value': max_value,
                'color_ramp': color_ramp,
                'prefix': prefix,
                'color_prefix': color_prefix,
                'first_division': first_division,
                'units': units,
            }

            divisions = cls.generate_custom_color_ramp_divisions(**layer['color_ramp_division_kwargs'])

            for label in divisions.keys():
                if color_prefix in label and int(label.replace(color_prefix, '')) >= first_division:
                    legend_info['divisions'][float(divisions[label.replace(color_prefix, prefix)])] = divisions[
                        label]
            legend_info['divisions'] = collections.OrderedDict(
                sorted(legend_info['divisions'].items())
            )

        return legend_info

    @classmethod
    def build_geojson_layer(cls, geojson, layer_name, layer_title, layer_variable, layer_id='', visible=True,
                            public=True, selectable=False, plottable=False, has_action=False, extent=None,
                            popup_title=None, excluded_properties=None, show_download=False):
        """
        Build an MVLayer object with supplied arguments.
        Args:
            geojson(dict): Python equivalent GeoJSON FeatureCollection.
            layer_name(str): Name of GeoServer layer (e.g.: agwa:3a84ff62-aaaa-bbbb-cccc-1a2b3c4d5a6b7c8d-model_boundaries).
            layer_title(str): Title of MVLayer (e.g.: Model Boundaries).
            layer_variable(str): Variable type of the layer (e.g.: model_boundaries).
            layer_id(UUID, int, str): layer_id for non geoserver layer where layer_name may not be unique.
            visible(bool): Layer is visible when True. Defaults to True.
            public(bool): Layer is publicly accessible when app is running in Open Portal Mode if True. Defaults to True.
            selectable(bool): Enable feature selection. Defaults to False.
            plottable(bool): Enable "Plot" button on pop-up properties. Defaults to False.
            has_action(bool): Enable "Action" button on pop-up properties. Defaults to False.
            extent(list): Extent for the layer. Optional.
            popup_title(str): Title to display on feature popups. Defaults to layer title.
            excluded_properties(list): List of properties to exclude from feature popups.
            show_download(boolean): enable download geojson as shapefile. Default is False.

        Returns:
            MVLayer: the MVLayer object.
        """  # noqa: E501
        # Define default styles for layers
        style_map = cls.get_vector_style_map()

        # Bind geometry features to layer via layer name
        for feature in geojson['features']:
            feature['properties']['layer_name'] = layer_name

        mv_layer = cls._build_mv_layer(
            layer_source='GeoJSON',
            layer_id=layer_id,
            layer_name=layer_name,
            layer_title=layer_title,
            layer_variable=layer_variable,
            options=geojson,
            extent=extent,
            visible=visible,
            public=public,
            selectable=selectable,
            plottable=plottable,
            has_action=has_action,
            popup_title=popup_title,
            excluded_properties=excluded_properties,
            style_map=style_map,
            show_download=show_download,
        )

        return mv_layer

    @classmethod
    def build_wms_layer(cls, endpoint, layer_name, layer_title, layer_variable, viewparams=None, env=None,
                        visible=True, tiled=True, selectable=False, plottable=False, has_action=False, extent=None,
                        public=True, geometry_attribute='geometry', layer_id='', excluded_properties=None,
                        popup_title=None, color_ramp_division_kwargs=None, times=None):
        """
        Build an WMS MVLayer object with supplied arguments.
        Args:
            endpoint(str): URL to GeoServer WMS interface.
            layer_name(str): Name of GeoServer layer (e.g.: agwa:3a84ff62-aaaa-bbbb-cccc-1a2b3c4d5a6b7c8d-model_boundaries).
            layer_title(str): Title of MVLayer (e.g.: Model Boundaries).
            layer_variable(str): Variable type of the layer (e.g.: model_boundaries).
            layer_id(UUID, int, str): layer_id for non geoserver layer where layer_name may not be unique.
            viewparams(str): VIEWPARAMS string.
            env(str): ENV string.
            visible(bool): Layer is visible when True. Defaults to True.
            public(bool): Layer is publicly accessible when app is running in Open Portal Mode if True. Defaults to True.
            tiled(bool): Configure as tiled layer if True. Defaults to True.
            selectable(bool): Enable feature selection. Defaults to False.
            plottable(bool): Enable "Plot" button on pop-up properties. Defaults to False.
            has_action(bool): Enable "Action" button on pop-up properties. Defaults to False.
            extent(list): Extent for the layer. Optional.
            popup_title(str): Title to display on feature popups. Defaults to layer title.
            excluded_properties(list): List of properties to exclude from feature popups.
            geometry_attribute(str): Name of the geometry attribute. Defaults to "geometry".
            color_ramp_division_kwargs(dict): arguments from MapLayout.generate_custom_color_ramp_divisions
            times (list): List of time steps if layer is time-enabled. Times should be represented as strings in ISO 8601 format (e.g.: ["20210322T112511Z", "20210322T122511Z", "20210322T132511Z"]). Currently only supported in CesiumMapView.
        Returns:
            MVLayer: the MVLayer object.
        """  # noqa: E501
        # Build params
        params = {'LAYERS': layer_name}

        if tiled:
            params.update({
                'TILED': True,
                'TILESORIGIN': '0.0,0.0'
            })

        if viewparams:
            params['VIEWPARAMS'] = viewparams

        if env:
            params['ENV'] = env
        if times:
            times = json.dumps(times),
        # Build options
        options = {
            'url': endpoint,
            'params': params,
            'serverType': 'geoserver',
            'crossOrigin': 'anonymous',
        }
        if color_ramp_division_kwargs:
            # Create color ramp and add them to ENV
            color_ramp_divisions = cls.generate_custom_color_ramp_divisions(**color_ramp_division_kwargs)
            if 'ENV' in params.keys():
                if params['ENV']:
                    params['ENV'] += ";" + cls.build_param_string(**color_ramp_divisions)
                else:
                    params['ENV'] = cls.build_param_string(**color_ramp_divisions)
            else:
                params['ENV'] = cls.build_param_string(**color_ramp_divisions)
        layer_source = 'TileWMS' if tiled else 'ImageWMS'

        if tiled:
            options['tileGrid'] = cls.DEFAULT_TILE_GRID

        mv_layer = cls._build_mv_layer(
            layer_id=layer_id,
            layer_name=layer_name,
            layer_source=layer_source,
            layer_title=layer_title,
            layer_variable=layer_variable,
            options=options,
            extent=extent,
            visible=visible,
            public=public,
            selectable=selectable,
            plottable=plottable,
            has_action=has_action,
            popup_title=popup_title,
            excluded_properties=excluded_properties,
            geometry_attribute=geometry_attribute,
            times=times,
        )

        return mv_layer

    # TODO: clean up kwargs
    @classmethod
    def build_arc_gis_layer(cls, endpoint, layer_name, layer_title, layer_variable, viewparams=None, env=None,
                            visible=True, tiled=True, selectable=False, plottable=False, has_action=False,
                            extent=None, public=True, geometry_attribute='geometry', layer_id='',
                            excluded_properties=None, popup_title=None):
        """
        Build an AcrGIS Map Server MVLayer object with supplied arguments.
        Args:
            endpoint(str): URL to GeoServer WMS interface.
            layer_name(str): Name of GeoServer layer (e.g.: agwa:3a84ff62-aaaa-bbbb-cccc-1a2b3c4d5a6b7c8d-model_boundaries).
            layer_title(str): Title of MVLayer (e.g.: Model Boundaries).
            layer_variable(str): Variable type of the layer (e.g.: model_boundaries).
            layer_id(UUID, int, str): layer_id for non geoserver layer where layer_name may not be unique.
            viewparams(str): VIEWPARAMS string.
            env(str): ENV string.
            visible(bool): Layer is visible when True. Defaults to True.
            public(bool): Layer is publicly accessible when app is running in Open Portal Mode if True. Defaults to True.
            tiled(bool): Configure as tiled layer if True. Defaults to True.
            selectable(bool): Enable feature selection. Defaults to False.
            plottable(bool): Enable "Plot" button on pop-up properties. Defaults to False.
            has_action(bool): Enable "Action" button on pop-up properties. Defaults to False.
            extent(list): Extent for the layer. Optional.
            popup_title(str): Title to display on feature popups. Defaults to layer title.
            excluded_properties(list): List of properties to exclude from feature popups.
            geometry_attribute(str): Name of the geometry attribute. Defaults to "geometry".

        Returns:
            MVLayer: the MVLayer object.
        """  # noqa: E501
        # Build options
        options = {
            'url': endpoint,
            'serverType': 'geoserver',
            'crossOrigin': 'anonymous'
        }

        layer_source = 'TileArcGISRest'

        mv_layer = cls._build_mv_layer(
            layer_id=layer_id,
            layer_name=layer_name,
            layer_source=layer_source,
            layer_title=layer_title,
            layer_variable=layer_variable,
            options=options,
            extent=extent,
            visible=visible,
            public=public,
            selectable=selectable,
            plottable=plottable,
            has_action=has_action,
            popup_title=popup_title,
            excluded_properties=excluded_properties,
            geometry_attribute=geometry_attribute
        )

        return mv_layer

    @classmethod
    def generate_custom_color_ramp_divisions(cls, min_value, max_value, num_divisions=10, value_precision=2,
                                             first_division=1, top_offset=0, bottom_offset=0, prefix='val',
                                             color_ramp=None, color_prefix='color', no_data_value=None):
        """
        Generate custom elevation divisions.
    
        Args:
            min_value (float): minimum value.
            max_value (float): maximum value.
            num_divisions (int): number of divisions.
            value_precision (int): level of precision for legend values.
            first_division (int): first division number (defaults to 1).
            top_offset (float): offset from top of color ramp (defaults to 0).
            bottom_offset (float): offset from bottom of color ramp (defaults to 0).
            prefix (str): name of division variable prefix (i.e.: 'val' for pattern 'val1').
            color_ramp (str): color ramp name in COLOR_RAMPS dict. Options are ['Blue', 'Blue and Red', 'Flower Field', 'Galaxy Berries', 'Heat Map', 'Olive Harmony', 'Mother Earth', 'Rainforest Frogs', 'Retro FLow', 'Sunset Fade'].
            color_prefix (str): name of color variable prefix (i.e.: 'color' for pattern 'color1').
            no_data_value (str): set no data value for the color ramp. (defaults to None).
        
        Returns:
            dict<name, value>: Color ramp division names and values.
        """  # noqa: E501
        divisions = {}

        # Equation of a Line
        max_div = first_division + num_divisions - 1
        min_div = first_division
        max_val = float(max_value - top_offset)
        min_val = float(min_value + bottom_offset)
        y2_minus_y1 = max_val - min_val
        x2_minus_x1 = max_div - min_div
        m = y2_minus_y1 / x2_minus_x1
        b = max_val - (m * max_div)

        for i in range(min_div, max_div + 1):
            divisions[f'{prefix}{i}'] = f"{(m * i + b):.{value_precision}f}"

            if color_ramp in cls.COLOR_RAMPS.keys():
                divisions[f'{color_prefix}{i}'] =\
                    f"{cls.COLOR_RAMPS[color_ramp][(i - first_division) % len(cls.COLOR_RAMPS[color_ramp])]}"
            else:
                # use default color ramp
                divisions[f'{color_prefix}{i}'] =\
                    f"{cls.COLOR_RAMPS['Default'][(i - first_division) % len(cls.COLOR_RAMPS['Default'])]}"
        if no_data_value is not None:
            divisions['val_no_data'] = no_data_value
        return divisions
