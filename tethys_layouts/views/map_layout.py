"""
********************************************************************************
* Name: map_layout.py
* Author: nswain
* Created On: June 24, 2021
* Copyright: (c) Aquaveo 2021
********************************************************************************
"""
import collections
from io import BytesIO
import json
import logging
import os
import requests
import uuid
from zipfile import ZipFile

from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
import shapefile

from tethys_gizmos.gizmo_options import SlideSheet
from tethys_layouts.views.tethys_layout import TethysLayout
from tethys_sdk.permissions import has_permission, permission_required
from tethys_sdk.gizmos import ToggleSwitch, CesiumMapView

log = logging.getLogger(f'tethys.{__name__}')


class MapLayout(TethysLayout):
    """
    Controller for the MapLayout view. Pass kwargs matching property names to as_controller()
        to override their values and configure the MapLayout view.

    Recommended Properties:
        app (TethysApp): The class of the app contained in app.py.
        base_template (str): Template to use as base template. Recommend overriding this to be your app's base template. Defaults to "tethys_layouts/tethys_layout.html".
        map_manager_class (MapManager): A MapManager class that defines the map layers.
        map_subtitle (str): The subtitle to display on the MapLayout view.
        map_title (str): The title to display on the MapLayout view.

    Optional Properties:
        back_url (str): URL that will be added to the back button. No back button if not provided.
        cesium_ion_token (str): Cesium Ion API token. Required if map_type is "cesium_map_view". See: https://cesium.com/learn/cesiumjs-learn/cesiumjs-quickstart/
        default_disable_basemap (bool) Set to True to disable the basemap.
        geocode_api_key = An Open Cage Geocoding API key. Required to enable address search/geocoding feature. See: https://opencagedata.com/api#quickstart
        feature_selection_mutiselect (bool): Set to True to enable multi-selection when feature selection is enabled. Defaults to False.
        feature_selection_sensitivity (int): Feature selection sensitivity/relative search radius. Defaults to 4.
        layer_tab_name (str) Name of the "Layers" tab. Defaults to "Layers".
        map_type (str): Type of map gizmo to use. One of "tethys_map_view" or "cesium_map_view". Defaults to "tethys_map_view".
        properties_popup_enabled (bool): Set to False to disable the properties popup. Defaults to True.
        sds_setting_name (str): Name of a Spatial Dataset Service Setting in the app to pass to MapManager when initializing. The SDS will be retrieved as an engine and passed to the constructor of the MapManager using the kwarg "sds_engine".
        show_custom_layer (bool): Show the "Custom Layers" item in the Layers tree when True. Users can add WMS layers to the Custom Layers layer group dynamically. Defaults to True.
        show_legends (bool): Show the Legend tab. Defaults to False.
    """
    # Changing these will likely break the MapLayout
    template_name = 'tethys_layouts/map_layout/map_layout.html'
    http_method_names = ['get', 'post']
    _geocode_endpoint = 'http://api.opencagedata.com/geocode/v1/geojson'

    # Required Properties
    map_manager_class = None
    map_subtitle = ''  # TODO: just use layout_title and layout_subtitle?
    map_title = ''

    # Optional Properties
    cesium_ion_token = None
    default_disable_basemap = False
    geocode_api_key = None
    feature_selection_mutiselect = False
    feature_selection_sensitivity = 4
    layer_tab_name = 'Layers'
    map_type = 'tethys_map_view'
    properties_popup_enabled = True
    sds_setting_name = ''
    show_custom_layer = True
    show_legends = False

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

    def get_context(self, request, context, *args, **kwargs):
        """
        Create context for the Map Layout view.

        Args:
            request (HttpRequest): The request.
            context (dict): The context dictionary.

        Returns:
            dict: modified context dictionary.
        """  # noqa: E501
        # Get the MapManager
        map_manager = self.get_map_manager()

        # Get additional kwargs for compose_map()
        compose_map_kwargs = self.get_compose_map_kwargs(request, *args, **kwargs)
        if not isinstance(compose_map_kwargs, dict):
            raise TypeError('The get_compose_map_kwargs() method must return a dictionary.')

        # Compose the Map
        map_view, map_extent, layer_groups = map_manager.compose_map(
            request=request,
            **compose_map_kwargs,
            *args, **kwargs
        )

        map_view = self.configure_map_view(args, kwargs, layer_groups, map_extent, map_manager, map_view, request)

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
            'workspace': self._SpatialManager.WORKSPACE,  # TODO: what is this used for?
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

    def configure_map_view(self, args, kwargs, layer_groups, map_extent, map_manager, map_view, request):
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
            map_manager=map_manager,
            *args, **kwargs
        )
        # Configure feature selection
        map_view.feature_selection = {
            'multiselect': self.feature_selection_mutiselect,
            'sensitivity': self.feature_selection_sensitivity,
        }
        # Create the Custom Layers layer group
        self.create_custom_layers_layer_group(layer_groups, map_manager)
        # Override MapView with CesiumMapView if Cesium is the chosen map_type.
        if self.map_type == "cesium_map_view":
            map_view = self.build_ceisum_map_view(map_view)
        return map_view

    # View Utilities -------------------------------------------------------- #
    def build_ceisum_map_view(self, map_view):
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
        layers, entities = self.translate_layers_to_cesium(map_view.layers)

        # Build CesiumMapView
        CesiumMapView.cesium_version = "1.74"
        cesium_map_view = CesiumMapView(
            cesium_ion_token=self.ceisum_ion_token,
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

    def translate_layers_to_cesium(self, map_view_layers):
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

    def create_custom_layers_layer_group(self, layer_groups, map_manager):
        """
        Create an empty layer group with display name "Custom Layers" if it does not already exist.

        Args:
            layer_groups (list<dict>): A list of layer group dictionaries.
            map_manager (MapManager): The MapManager instance for this MapLayout view.
        """
        # Check if we need to create a blank custom layer group
        create_custom_layer = True
        for layer_group in layer_groups:
            if layer_group['id'] == 'custom_layers':
                create_custom_layer = False
                break

        if create_custom_layer:
            custom_layers = map_manager.build_layer_group(
                id="custom_layers",
                display_name="Custom Layers",
                layers=[],
                layer_control='checkbox',
                visible=True
            )
            layer_groups.append(custom_layers)

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
        map_manager = self.get_map_manager()
        title, data, layout = map_manager.get_plot_for_layer_feature(layer_name, feature_id)

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
        # TODO: Should use map_manager._build_mv_layer or at the very least MVLayer
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
        # Get the MapManager
        map_manager = self.get_map_manager()

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

        divisions = map_manager.generate_custom_color_ramp_divisions(
            min_value=minimum,
            max_value=maximum,
            color_ramp=color_ramp, prefix=prefix,
            color_prefix=color_prefix,
            first_division=first_division
        )

        division_string = map_manager.build_param_string(**divisions)
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
        # Get MapManager instance
        map_manager = self.get_map_manager()

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
            layers.append(map_manager._build_mv_layer(
                layer_source="GeoJSON",
                layer_name=layer_ids[i],
                layer_title=layer_names[i],
                layer_variable=layer_legends[i],
                options=None,
            ))

        # Build Layer groups
        layer_group = map_manager.build_layer_group(layer_group_id, layer_group_name, layers=layers)
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
        if not self.geocode_api_key:
            raise RuntimeError('Can not run GeoCode query because no API token was supplied. Please provide the '
                               'API key via the "geocode_api_key" attribute of the MapLayoutView.')

        json_data = json.loads(request.POST.get('data', ''))
        layer_id = request.POST.get('id', '0')
        json_type = json_data['features'][0]['geometry']['type']
        if json_type == 'Polygon':
            shpfile_obj = shapefile.Writer(shapefile.POLYGON)
        elif json_type == 'Point':
            shpfile_obj = shapefile.Writer(shapefile.POINT)
        elif json_type == 'LineString':
            shpfile_obj = shapefile.Writer(shapefile.POLYLINE)

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
                shpfile_obj.poly(parts=geo)
            elif json_type == 'Point':
                shpfile_obj.point(geo[0], geo[1])
            elif json_type == 'LineString':
                shpfile_obj.line(parts=[geo])

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

        # Hooks ------------------------------------------------------------- #
        def get_map_manager(self):
            """
            Hook for overriding how the MapManager is created (e.g.: pass custom arguments).

            Args:
                request (HttpRequest): The request.

            Returns:
                map_manager (MapManager): Map Manager instance
            """  # noqa: E501
            # TODO: Internalize SpatialManager into MapManager?
            if getattr(self, '_map_manager', None) is not None:
                return self._map_manager

            if self.sds_setting_name:
                sds_engine = self.app.get_spatial_dataset_service(self.sds_setting_name, as_engine=True)
                self._map_manager = self.map_manager_class(sds_engine=sds_engine)
            else:
                self._map_manager = self.map_manager_class()

            return self._map_manager

        def should_disable_basemap(self, request, map_manager, *args, **kwargs):
            """
            Hook to override disabling the basemap.

            Args:
                request (HttpRequest): The request.
                map_manager (MapManager): MapManager instance associated with this request.

            Returns:
                bool: True to disable the basemap.
            """
            return self.default_disable_basemap

        def get_compose_map_kwargs(self, request, *args, **kwargs):
            """
            Hook for specifying additional kwargs that should be passed to the MapManager.compose_map() call.

            Args:
                request (HttpRequest): The request.

            Returns:
                dict: keyword value pairs to be passed as kwargs to MapManager.compose_map().
            """
            return dict()
