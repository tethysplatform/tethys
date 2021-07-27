"""
********************************************************************************
* Name: map_layout.py
* Author: nswain
* Created On: June 24, 2021
* Copyright: (c) Aquaveo 2021
********************************************************************************
"""
from abc import ABCMeta
import collections
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

from tethys_layouts.exceptions import TethysLayoutPropertyException
from tethys_layouts.mixins.map_layout import MapLayoutMixin
from tethys_layouts.utilities import classproperty
from tethys_layouts.views.tethys_layout import TethysLayout
from tethys_sdk.permissions import has_permission, permission_required
from tethys_sdk.gizmos import ToggleSwitch, CesiumMapView, MapView, MVView, SlideSheet, SelectInput

log = logging.getLogger(f'tethys.{__name__}')


class MapLayout(TethysLayout, MapLayoutMixin):
    """
    Controller for the MapLayout view. Create a class that extends this class and implement the compose_layers method
        and other properties as desired. In the app.py pass MapLayout.as_controller() as the controller argument to
        the UrlMap. You may also pass kwargs matching property names of the class to MapLayout.as_controller() to
        override their values and configure the MapLayout view.

    Recommended Properties:
        app (TethysApp): The class of the app contained in app.py.
        base_template (str): Template to use as base template. Recommend overriding this to be your app's base
            template. Defaults to "tethys_layouts/tethys_layout.html".
        map_subtitle (str): The subtitle to display on the MapLayout view.
        map_title (str): The title to display on the MapLayout view.

    Optional Properties:
        back_url (str): URL that will be added to the back button. No back button if not provided.
        cesium_ion_token (str): Cesium Ion API token. Required if map_type is "cesium_map_view".
            See: https://cesium.com/learn/cesiumjs-learn/cesiumjs-quickstart/
        default_center (2-list<float>): Coordinates of the initial center for the map. Defaults to [-98.583, 39.833].
        default_disable_basemap (bool) Set to True to disable the basemap.
        default_zoom (int): Default zoom level. Defaults to 4.
        geocode_api_key = An Open Cage Geocoding API key. Required to enable address search/geocoding feature.
            See: https://opencagedata.com/api#quickstart
        geoserver_workspace = Name of the GeoServer workspace of layers if applicable. Defaults to None.
        initial_map_extent = The initial zoom extent for the map. Defaults to [-65.69, 23.81, -129.17, 49.38].
        feature_selection_multiselect (bool): Set to True to enable multi-selection when feature selection is
            enabled. Defaults to False.
        feature_selection_sensitivity (int): Feature selection sensitivity/relative search radius. Defaults to 4.
        layer_tab_name (str) Name of the "Layers" tab. Defaults to "Layers".
        map_type (str): Type of map gizmo to use. One of "tethys_map_view" or "cesium_map_view". Defaults
            to "tethys_map_view".
        max_zoom (int): Maximum zoom level. Defaults to 28.
        min_zoom (int): Minimum zoom level. Defaults to 0.
        properties_popup_enabled (bool): Set to False to disable the properties popup. Defaults to True.
        sds_setting_name (str): Name of a Spatial Dataset Service Setting in the app to pass to MapManager when
            initializing. The SDS will be retrieved as an engine and passed to the constructor of the MapManager
                using the kwarg "sds_engine".
        show_custom_layer (bool): Show the "Custom Layers" item in the Layers tree when True. Users can add WMS
            layers to the Custom Layers layer group dynamically. Defaults to True.
        show_legends (bool): Show the Legend tab. Defaults to False.
        show_public_toggle (bool): Show the "Public/Private" toggle control in the layer context menus.
        wide_nav (bool): Render Layout with a wider navigation menu on left. Defaults to False.
    """
    __metaclass__ = ABCMeta

    # Changing these will likely break the MapLayout
    template_name = 'tethys_layouts/map_layout/map_layout.html'
    http_method_names = ['get', 'post']
    _geocode_endpoint = 'http://api.opencagedata.com/geocode/v1/geojson'

    # Required Properties
    map_subtitle = ''
    map_title = ''

    # Optional Properties
    cesium_ion_token = None
    default_center = [-98.583, 39.833]  # USA Center
    default_disable_basemap = False
    default_zoom = 4
    geocode_api_key = None
    geoserver_workspace = ''
    initial_map_extent = [-65.69, 23.81, -129.17, 49.38]  # USA EPSG:2374
    feature_selection_multiselect = False
    feature_selection_sensitivity = 4
    layer_tab_name = 'Layers'
    map_type = 'tethys_map_view'
    max_zoom = 28
    min_zoom = 0
    properties_popup_enabled = True
    sds_setting_name = ''
    show_custom_layer = False
    show_legends = False
    show_public_toggle = False
    wide_nav = False

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
    def sds_setting(cls):
        if not cls.sds_setting_name:
            raise TethysLayoutPropertyException('sds_setting_name', MapLayout)
        if not cls.app:
            log.debug(f'MapLayout.app: {cls.app}')
            raise TethysLayoutPropertyException('app', MapLayout)
        return cls.app.get_spatial_dataset_service(cls.sds_setting_name)

    # Methods to Override  -------------------------------------------------- #
    def compose_layers(self, request, map_view, *args, **kwargs):
        """
        Compose layers and layer groups for the MapLayout and add to the given MapView. Use the built-in
            utility methods to build the MVLayer objects and layer group dictionaries. Returns a list of
            layer group dictionaries.

        Args:
            request(HttpRequest): A Django request object.
            map_view(MapView): The MapView gizmo to add layers to.

        Returns:
            list<LayerGroupDicts>: The MapView, extent, and list of LayerGroup dictionaries.
        """
        return []

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
        log.debug('Building MapView...')
        map_view = self._build_map_view(request, *args, **kwargs)

        # Add layers to the Map
        log.debug('Composing layers...')
        layer_groups = self.compose_layers(request=request, map_view=map_view, *args, **kwargs)
        log.debug(f'Number of Layers: {len(map_view.layers)}')

        # Check if we need to create a blank custom layer group
        create_custom_layer = True
        for layer_group in layer_groups:
            if layer_group['id'] == 'custom_layers':
                create_custom_layer = False
                break

        # Create the Custom Layers layer group
        if create_custom_layer:
            log.debug('Creating the "Custom Layers" layer group...')
            custom_layers = self.build_layer_group(
                id="custom_layers",
                display_name="Custom Layers",
                layers=[],
                layer_control='checkbox',
                visible=True
            )
            layer_groups.append(custom_layers)

        # Build legends
        log.debug('Building legends for each layer...')
        legends = []
        for layer in map_view.layers:
            legend = self.build_legend(layer)
            if legend is not None:
                # Create color ramp selector
                legend_select_input = SelectInput(
                    name=f'tethys-color-ramp-picker-{legend["legend_id"]}',
                    options=legend.get('select_options'),
                    initial=legend.get('initial_option'),
                    classes='map-layout-color-ramp-picker',
                    original=True,
                )
                legends.append((legend, legend_select_input))

        # Override MapView with CesiumMapView if Cesium is the chosen map_type.
        if self.map_type == "cesium_map_view":
            log.debug('Converting MapView to CesiumMapView...')
            map_view = self._build_ceisum_map_view(map_view)

        # Prepare context
        context.update({
            'enable_properties_popup': self.properties_popup_enabled,
            'geocode_enabled': self.geocode_api_key is not None,
            'layer_groups': layer_groups,
            'layer_tab_name': self.layer_tab_name,
            'legends': legends,
            'map_extent': self.map_extent,
            'map_type': self.map_type,
            'map_view': map_view,
            'nav_subtitle': self.map_subtitle,
            'nav_title': self.map_title,
            'show_custom_layer': self.show_custom_layer,
            'show_legends': self.show_legends,
            'wide_nav': self.wide_nav,
            'workspace': self.geoserver_workspace,
        })

        if context.get('show_public_toggle', False):
            layer_dropdown_toggle = ToggleSwitch(
                display_text='',
                name='layer-dropdown-toggle',
                on_label='Yes',
                off_label='No',
                on_style='success',
                off_style='danger',
                initial=True,
                size='small',
                classes='layer-dropdown-toggle'
            )
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
            'show_public_toggle': self.show_public_toggle and has_permission(request, 'toggle_public_layers'),
            'show_remove': has_permission(request, 'remove_layers'),
            'show_rename': has_permission(request, 'rename_layers'),
        }
        return permissions

    # Private View Helpers -------------------------------------------------- #
    def _build_map_view(self, request, *args, **kwargs):
        """
        Build the MapView gizmo.

        Args:
            request (HttpRequest): The request.

        Returns:
            MapView: the MapView gizmo.
        """
        map_view = MapView(
            height='100%',
            width='100%',
            controls=[
                'Rotate',
                'FullScreen',
                {'ZoomToExtent': {
                    'projection': 'EPSG:4326',
                    'extent': self.map_extent
                }}
            ],
            layers=[],
            view=self.default_view,
            basemap=[
                'Stamen',
                {'Stamen': {'layer': 'toner', 'control_label': 'Black and White'}},
                'OpenStreetMap',
                'ESRI',
            ],
            legend=False
        )

        # Configure initial basemap visibility
        map_view.disable_basemap = self.should_disable_basemap(
            request=request,
            *args, **kwargs
        )

        # Configure feature selection
        map_view.feature_selection = {
            'multiselect': self.feature_selection_multiselect,
            'sensitivity': self.feature_selection_sensitivity,
        }

        return map_view

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
        # TODO: Implement a method that does not require the database. JSON File? Local storage?
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
                # TODO: Implement a method that does not require the database. JSON File? Local storage?
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
            Credit to: https://github.com/TipsForGIS/geoJSONToShpFile/blob/master/geoJ.py

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
        wms_endpoint = cls.sds_setting.public_endpoint if public else cls.sds_setting.endpoint
        wms_endpoint = wms_endpoint.replace('rest', 'wms')

        # Add trailing slash for consistency.
        if wms_endpoint[-1] != '/':
            wms_endpoint += '/'
        return wms_endpoint
