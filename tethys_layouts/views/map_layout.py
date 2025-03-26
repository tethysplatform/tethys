"""
********************************************************************************
* Name: map_layout.py
* Author: nswain
* Created On: June 24, 2021
* Copyright: (c) Aquaveo 2021
********************************************************************************
"""

from tethys_portal.optional_dependencies import optional_import
from abc import ABCMeta
import collections
from io import BytesIO
import json
import logging
from pathlib import Path
import requests
import tempfile
import uuid
from zipfile import ZipFile

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.utils.functional import classproperty

from tethys_layouts.exceptions import TethysLayoutPropertyException
from tethys_layouts.mixins.map_layout import MapLayoutMixin
from tethys_layouts.views.tethys_layout import TethysLayout
from tethys_sdk.permissions import has_permission
from tethys_sdk.gizmos import (
    ToggleSwitch,
    CesiumMapView,
    MapView,
    MVView,
    SlideSheet,
    SelectInput,
)

# optional imports
shapefile = optional_import("shapefile")  # PyShp

log = logging.getLogger(f"tethys.{__name__}")


class MapLayout(TethysLayout, MapLayoutMixin):
    """
    Controller for the MapLayout view. Create a class that extends this class and implement the ``compose_layers`` method and other properties as desired. Decorate the class using the ``controller`` decorator to map it to a URL.

    Attributes:
        app (TethysApp): The class of the app contained in app.py.
        back_url (str): URL that will be added to the back button. No back button if not provided.
        basemaps (list or str): Name of a basemap or list of basemaps that will be available on the map. Same as the MapView gizmo basemap argument. Does not apply to the Cesium renderer.
        base_template (str): Template to use as base template. Recommend overriding this to be your app's base template. Defaults to "tethys_layouts/tethys_layout.html".
        cesium_ion_token (str): Cesium Ion API token. Required if map_type is "cesium_map_view". See: https://cesium.com/learn/cesiumjs-learn/cesiumjs-quickstart/
        default_disable_basemap (bool) Set to True to disable the basemap.
        default_map_extent = The default BBOX extent for the map. Defaults to [-65.69, 23.81, -129.17, 49.38].
        enforce_permissions (bool): Enables permissions checks when True. Defaults to False.
        geocode_api_key (str): An Open Cage Geocoding API key. Required to enable address search/geocoding feature. See: https://opencagedata.com/api#quickstart
        geocode_extent (4-list): Bounding box defining search area for address search feature (e.g.: [-65.69, 23.81, -129.17, 49.38]). Alternatively, set to 'map-extent' to use map extent.
        geoserver_workspace (str): Name of the GeoServer workspace of layers if applicable. Defaults to None.
        feature_selection_multiselect (bool): Set to True to enable multi-selection when feature selection is enabled. Defaults to False.
        feature_selection_sensitivity (int): Feature selection sensitivity/relative search radius. Defaults to 4.
        layer_tab_name (str) Name of the "Layers" tab. Defaults to "Layers".
        map_subtitle (str): The subtitle to display on the MapLayout view.
        map_title (str): The title to display on the MapLayout view.
        map_type (str): Type of map gizmo to use. One of "tethys_map_view" or "cesium_map_view". Defaults to "tethys_map_view".
        max_zoom (int): Maximum zoom level. Defaults to 28.
        min_zoom (int): Minimum zoom level. Defaults to 0.
        plot_slide_sheet (bool): Enables the Plotly slide sheet when True. Defaults to False. The slide sheet can be opened and populated using the JavaScript API.
        plotly_version (str): Version of Plotly library to load for Plotly slide sheet. Defaults to "2.3.0".
        sds_setting_name (str): Name of a Spatial Dataset Service Setting in the app to pass to MapManager when initializing. The SDS will be retrieved as an engine and passed to the constructor of the MapManager using the kwarg "sds_engine".
        show_custom_layer (bool): Show the "Custom Layers" item in the Layers tree when True. Users can add WMS layers to the Custom Layers layer group dynamically. Defaults to True.
        show_legends (bool): Show the Legend tab. Defaults to False.
        show_map_clicks (bool): Show where the user clicks when they click on the map. Defaults to False.
        show_map_click_popup (bool): Display a pop-up pointing to the point where user clicks. Defaults to False.
        show_properties_popup (bool): Show popup with feature properties when True. Defaults to False.
        show_public_toggle (bool): Show the "Public/Private" toggle control in the layer context menus.
        wide_nav (bool): Render Layout with a wider navigation menu on left. Defaults to False.

    """  # noqa:E501

    __metaclass__ = ABCMeta

    # Changing these will likely break the MapLayout
    template_name = "tethys_layouts/map_layout/map_layout.html"
    http_method_names = ["get", "post"]
    _geocode_endpoint = "http://api.opencagedata.com/geocode/v1/geojson"

    # Required Properties
    map_subtitle = ""
    map_title = ""

    # Optional Properties
    basemaps = ["OpenStreetMap", "ESRI"]
    cesium_ion_token = None
    default_disable_basemap = False
    default_map_extent = [-65.69, 23.81, -129.17, 49.38]  # USA EPSG:4326
    geocode_api_key = None
    enforce_permissions = False
    geocode_extent = None
    geoserver_workspace = ""
    feature_selection_multiselect = False
    feature_selection_sensitivity = 4
    layer_tab_name = "Layers"
    map_type = "tethys_map_view"
    max_zoom = 28
    min_zoom = 0
    plot_slide_sheet = False
    plotly_version = "2.3.0"
    sds_setting_name = ""
    show_custom_layer = False
    show_legends = False
    show_map_clicks = False
    show_map_click_popup = False
    show_properties_popup = False
    show_public_toggle = False
    wide_nav = False

    @classproperty
    def sds_setting(cls):
        if not cls.sds_setting_name:
            raise TethysLayoutPropertyException("sds_setting_name", MapLayout)
        if not cls.app:
            log.debug(f"MapLayout.app: {cls.app}")
            raise TethysLayoutPropertyException("app", MapLayout)
        return cls.app.get_spatial_dataset_service(cls.sds_setting_name)

    # Methods to Override  -------------------------------------------------- #
    def compose_layers(self, request, map_view, *args, **kwargs):
        """
        Compose layers and layer groups for the MapLayout and add to the given MapView. Use the built-in utility methods to build the MVLayer objects and layer group dictionaries. Returns a list of layer group dictionaries.

        Args:
            request(HttpRequest): A Django request object.
            map_view(MapView): The MapView gizmo to add layers to.
            layer_data (dict): The MVLayer.data dictionary.
            feature_props (dict): The properties of the selected feature.

        Returns:
            list<LayerGroupDicts>: The MapView, extent, and list of LayerGroup dictionaries.
        """  # noqa:E501
        return list()

    def build_map_extent_and_view(self, request, *args, **kwargs):
        """
        Builds the default MVView and BBOX extent for the map.

        Returns:
            MVView, 4-list<float>: default view and extent of the project.
        """
        extent = self.default_map_extent

        # Construct the default view
        view = MVView(
            projection="EPSG:4326",
            extent=extent,
            maxZoom=self.max_zoom,
            minZoom=self.min_zoom,
        )

        return view, extent

    def get_plot_for_layer_feature(
        self,
        request,
        layer_name,
        feature_id,
        layer_data,
        feature_props,
        *args,
        **kwargs,
    ):
        """
        Retrieves plot data for given feature on given layer.

        Args:
            request(HttpRequest): A Django request object.
            layer_name(str): Name/id of layer.
            feature_id(str): Feature ID of feature.
            layer_data(dict): Data attached to the layer with the data argument.
            feature_props(dict): Feature type properties.

        Returns:
            str, list<dict>, dict: plot title, data series, and layout options, respectively.
        """
        layout = {"xaxis": {"title": layer_name}, "yaxis": {"title": "Undefined"}}

        data = [
            {
                "name": feature_id,
                "mode": "lines",
                "x": [1, 2, 3, 4],
                "y": [10, 15, 13, 17],
            }
        ]
        return "Undefined", data, layout

    @classmethod
    def get_vector_style_map(cls):
        """
        Builds the style map for vector layers.

        Returns:
            dict: the style map.
        """
        color = "navy"
        style_map = {
            "Point": {
                "ol.style.Style": {
                    "image": {
                        "ol.style.Circle": {
                            "radius": 5,
                            "fill": {
                                "ol.style.Fill": {
                                    "color": color,
                                }
                            },
                            "stroke": {
                                "ol.style.Stroke": {
                                    "color": color,
                                }
                            },
                        }
                    }
                }
            },
            "LineString": {
                "ol.style.Style": {
                    "stroke": {"ol.style.Stroke": {"color": color, "width": 2}}
                }
            },
            "Polygon": {
                "ol.style.Style": {
                    "stroke": {"ol.style.Stroke": {"color": color, "width": 2}},
                    "fill": {"ol.style.Fill": {"color": "rgba(0, 0, 255, 0.1)"}},
                }
            },
            "MultiPolygon": {
                "ol.style.Style": {
                    "stroke": {"ol.style.Stroke": {"color": color, "width": 2}},
                    "fill": {"ol.style.Fill": {"color": "rgba(0, 0, 255, 0.1)"}},
                }
            },
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

    def on_add_custom_layer(self, request, *args, **kwargs):
        """
        Implement this method to handle AJAX method that persists custom layers added to map by user.

        Args:
            request(HttpRequest): The request.

        Returns:
            JsonResponse: success.
        """
        return JsonResponse({"success": False, "message": "Not Implemented."})

    def on_rename_tree_item(self, request, *args, **kwargs):
        """
        Implement this method to persist "rename" actions on layers and layer groups.

        Args:
            request(HttpRequest): The request.

        Returns:
            JsonResponse: with keys "success" (bool) and "message" (str).
        """
        return JsonResponse({"success": False, "message": "Not Implemented."})

    def on_remove_tree_item(self, request, *args, **kwargs):
        """
        Implement this method to persist "remove" actions on layers and layer groups.

        Args:
            request(HttpRequest): The request.

        Returns:
            JsonResponse: with keys "success" (bool) and "message" (str).
        """
        return JsonResponse({"success": False, "message": "Not Implemented."})

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
        # Build MVView and extent
        view, extent = self.build_map_extent_and_view(request, *args, **kwargs)

        # Compose the Map
        log.debug("Building MapView...")
        map_view = self._build_map_view(request, view, extent, *args, **kwargs)

        # Add layers to the Map
        log.debug("Composing layers...")
        layer_groups = self.compose_layers(
            *args, request=request, map_view=map_view, **kwargs
        )
        # Add layers to map view if not already added
        for layer_group in layer_groups:
            for layer in layer_group["layers"]:
                if layer not in map_view.layers:
                    map_view.layers.append(layer)

        log.debug(f"Number of Layers: {len(map_view.layers)}")

        # Check if we need to create a blank custom layer group
        create_custom_layer = True
        for layer_group in layer_groups:
            if layer_group["id"] == "custom_layers":
                create_custom_layer = False
                break

        # Create the Custom Layers layer group
        if self.show_custom_layer and create_custom_layer:
            log.debug('Creating the "Custom Layers" layer group...')
            custom_layers = self.build_custom_layer_group()
            layer_groups.append(custom_layers)

        # Build legends
        log.debug("Building legends for each layer...")
        legends = []
        for layer in map_view.layers:
            if not layer.data["show_legend"]:
                continue

            legend = self.build_legend(layer)
            if legend is not None:
                legend_select_options = legend.get("select_options")  # None if not set
                if legend_select_options:
                    # Create color ramp selector
                    legend_select_input = SelectInput(
                        name=f'tethys-color-ramp-picker-{legend["legend_id"]}',
                        options=legend.get("select_options"),
                        initial=legend.get("initial_option"),
                        classes="map-layout-color-ramp-picker form-select-sm",
                        original=True,
                    )
                else:
                    legend_select_input = None

                legends.append((legend, legend_select_input))

        # Override MapView with CesiumMapView if Cesium is the chosen map_type.
        if self.map_type == "cesium_map_view":
            log.debug("Converting MapView to CesiumMapView...")
            map_view = self._build_ceisum_map_view(map_view)

        # Prepare context
        context.update(
            {
                "geocode_enabled": self.geocode_api_key is not None,
                "layer_groups": layer_groups,
                "layer_tab_name": self.layer_tab_name,
                "legends": legends,
                "map_extent": extent,
                "map_type": self.map_type,
                "map_view": map_view,
                "nav_subtitle": self.map_subtitle,
                "nav_title": self.map_title,
                "plotly_version": self.plotly_version,
                "show_custom_layer": self.show_custom_layer,
                "show_properties_popup": self.show_properties_popup,
                "show_map_click_popup": self.show_map_click_popup,
                "show_legends": self.show_legends,
                "wide_nav": self.wide_nav,
                "workspace": self.geoserver_workspace,
            }
        )

        if context.get("show_public_toggle", False):
            layer_dropdown_toggle = ToggleSwitch(
                display_text="",
                name="layer-dropdown-toggle",
                on_label="Yes",
                off_label="No",
                on_style="success",
                off_style="danger",
                initial=True,
                size="small",
                classes="layer-dropdown-toggle",
            )
            context.update({"layer_dropdown_toggle": layer_dropdown_toggle})

        # Add plot slide sheet
        plot_slidesheet = SlideSheet(
            id="plot-slide-sheet",
            title="Plot",
            content_template="tethys_layouts/map_layout/map_plot.html",
        )

        context.update({"plot_slide_sheet": plot_slidesheet})
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
        map_permissions = {
            "can_download": not self.enforce_permissions
            or has_permission(request, "can_download"),
            "can_use_geocode": not self.enforce_permissions
            or has_permission(request, "use_map_geocode"),
            "can_use_plot": self.plot_slide_sheet
            and (
                not self.enforce_permissions or has_permission(request, "use_map_plot")
            ),
            "show_public_toggle": self.show_public_toggle
            and (
                not self.enforce_permissions
                or has_permission(request, "toggle_public_layers")
            ),
            "show_remove": not self.enforce_permissions
            or has_permission(request, "remove_layers"),
            "show_rename": not self.enforce_permissions
            or has_permission(request, "rename_layers"),
        }
        return map_permissions

    # Private View Helpers -------------------------------------------------- #
    def _build_map_view(self, request, view, extent, *args, **kwargs):
        """
        Build the MapView gizmo.

        Args:
            request (HttpRequest): The request.
            view (MVView): The MVView that defines the initial view of the map.
            extent (4-list<float>): Map extent for home button (e.g.: [-180, 180, -90, 90]).

        Returns:
            MapView: the MapView gizmo.
        """
        map_view = MapView(
            height="100%",
            width="100%",
            controls=[
                "Rotate",
                "FullScreen",
                {
                    "ZoomToExtent": {
                        "projection": "EPSG:4326",
                        "extent": extent,
                    }
                },
            ],
            layers=[],
            view=view,
            basemap=self.basemaps,
            legend=False,
            show_clicks=self.show_map_clicks,
        )

        # Configure initial basemap visibility
        map_view.disable_basemap = self.should_disable_basemap(
            *args, request=request, **kwargs
        )

        # Configure feature selection
        map_view.feature_selection = {
            "multiselect": self.feature_selection_multiselect,
            "sensitivity": self.feature_selection_sensitivity,
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
            raise RuntimeError(
                'You must set the "cesium_ion_token" attribute of the '
                'MapLayout to use the Cesium "map_type".'
            )

        # Translate the MapView.layers into Cesium layers and entities
        layers, entities = self._translate_layers_to_cesium(map_view.layers)

        # Build CesiumMapView
        CesiumMapView.cesium_version = "1.74"
        cesium_map_view = CesiumMapView(
            cesium_ion_token=self.cesium_ion_token,
            options={
                "contextOptions": {
                    "webgl": {
                        "xrCompatible": True,
                        "alpha": True,
                        "preserveDrawingBuffer": True,
                    }
                },
                "vrButton": False,
                "scene3DOnly": True,
            },
            terrain={
                "terrainProvider": {
                    "Cesium.createWorldTerrain": {
                        "requestVertexNormals": True,
                        "requestWaterMask": True,
                    }
                }
            },
            layers=layers,
            entities=entities,
        )
        return cesium_map_view

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
            if layer["source"] in ["ImageWMS", "TileWMS"]:
                cesium_layers.append(layer)
            elif layer["source"] in ["GeoJSON"]:
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
        layer_name = request.POST.get("layer_name", "")
        feature_id = request.POST.get("feature_id", "")
        layer_data = json.loads(request.POST.get("layer_data", "{}"))
        feature_props = json.loads(request.POST.get("feature_props", "{}"))

        # Initialize MapManager
        title, data, layout = self.get_plot_for_layer_feature(
            request, layer_name, feature_id, layer_data, feature_props, *args, **kwargs
        )

        return JsonResponse({"title": title, "data": data, "layout": layout})

    def build_legend_item(self, request, *args, **kwargs):
        """
        A jQuery.load() handler method that renders the HTML for a legend.
        """
        # Get request parameters
        legend_div_id = request.POST.get("div_id")
        minimum = json.loads(request.POST.get("minimum"))
        maximum = json.loads(request.POST.get("maximum"))
        color_ramp = request.POST.get("color_ramp")
        prefix = request.POST.get("prefix")
        color_prefix = request.POST.get("color_prefix")
        first_division = json.loads(request.POST.get("first_division"))
        layer_id = request.POST.get("layer_id")

        legend = {
            "divisions": dict(),
        }

        divisions = self.generate_custom_color_ramp_divisions(
            min_value=minimum,
            max_value=maximum,
            color_ramp=color_ramp,
            prefix=prefix,
            color_prefix=color_prefix,
            first_division=first_division,
        )

        division_string = self.build_param_string(**divisions)
        for label in divisions.keys():
            if (
                color_prefix in label
                and int(label.replace(color_prefix, "")) >= first_division
            ):
                legend["divisions"][
                    float(divisions[label.replace(color_prefix, prefix)])
                ] = divisions[label]

        legend["divisions"] = collections.OrderedDict(
            sorted(legend["divisions"].items())
        )

        r = render(
            request,
            "tethys_layouts/map_layout/color_ramp_component.html",
            {"legend": legend},
        )

        html_str = str(r.content, "utf-8")
        response = JsonResponse(
            {
                "success": True,
                "response": html_str,
                "div_id": legend_div_id,
                "color_ramp": color_ramp,
                "division_string": division_string,
                "layer_id": layer_id,
            }
        )
        return response

    def build_layer_tree_item(self, request, *args, **kwargs):
        """
        A jQuery.loads() handler that renders the HTML for a layer group tree item.

        operation (create/append): create is create a whole new layer group with all the layer items associated with it
            append is append an associated layer into an existing layer group
        """
        try:
            # Get request parameters
            operation = request.POST.get("operation", "create")
            layer_group_name = request.POST.get("layer_group_name")
            layer_group_id = request.POST.get("layer_group_id")
            layer_names = json.loads(request.POST.get("layer_names"))
            layer_ids = json.loads(request.POST.get("layer_ids"))
            layer_legends = json.loads(request.POST.get("layer_legends"))
            show_rename = json.loads(request.POST.get("show_rename", "true"))
            show_remove = json.loads(request.POST.get("show_remove", "true"))
            show_download = json.loads(request.POST.get("show_download", "false"))
            layers = []

            # Reconstruct the MVLayer objects
            for i in range(len(layer_names)):
                layers.append(
                    self._build_mv_layer(
                        layer_source="GeoJSON",
                        layer_name=layer_ids[i],
                        layer_title=layer_names[i],
                        layer_variable=layer_legends[i],
                        options=None,
                        renamable=show_rename,
                        removable=show_remove,
                    )
                )

            # Build Layer groups
            layer_group = self.build_layer_group(
                layer_group_id, layer_group_name, layers=layers
            )
            context = {
                "layer_group": layer_group,
                "show_rename": show_rename,
                "show_remove": show_remove,
                "show_download": show_download,
            }

            if operation == "create":
                template = "tethys_layouts/map_layout/layer_group_content.html"
            else:
                # Only works for one layer at a time for now.
                template = "tethys_layouts/map_layout/layer_item_content.html"
                context["layer"] = layers[0]

            r = render(request, template, context)

            html_str = str(r.content, "utf-8")
            return JsonResponse({"success": True, "response": html_str})
        except Exception:
            log.exception("An unexpected error has occurred.")
            return JsonResponse(
                {"success": False, "error": "An unexpected error has occurred."}
            )

    def find_location_by_query(self, request, *args, **kwargs):
        """ "
        An AJAX handler that performs geocoding queries.

        Args:
            request(HttpRequest): The request.
        """
        if self.enforce_permissions and not has_permission(request, "use_map_geocode"):
            json = {
                "success": False,
                "error": "Permission Denied: user does not have permission to use geocoding.",
            }
            return JsonResponse(json)

        if not self.geocode_api_key:
            raise RuntimeError(
                "Cannot run GeoCode query because no API token was supplied. Please provide the "
                'API key via the "geocode_api_key" attribute of the MapLayoutView.'
            )

        query = request.POST.get("q", None)

        params = {"query": query, "key": self.geocode_api_key}

        if isinstance(self.geocode_extent, (list, tuple)):
            geocode_extent = [str(i) for i in self.geocode_extent]
            params["bounds"] = ",".join(geocode_extent)

        response = requests.get(url=self._geocode_endpoint, params=params)

        if response.status_code != 200:
            json = {"success": False, "error": response.text}
            return JsonResponse(json)

        # Construct friendly name for address select
        r_json = response.json()

        # Construct success json and parse out needed info
        json = {"success": True, "results": []}

        for address in r_json["features"]:
            point = address["geometry"]["coordinates"]
            scale = 0.001

            if "bounds" in address["properties"]:
                bounds = address["properties"]["bounds"]

                minx = float(bounds["southwest"]["lng"])
                maxx = float(bounds["northeast"]["lng"])
                miny = float(bounds["southwest"]["lat"])
                maxy = float(bounds["northeast"]["lat"])

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
            display_name = address["properties"]["formatted"]
            if len(display_name) > max_name_length:
                display_name = display_name[:max_name_length] + "..."

            geocode_id = uuid.uuid4()

            json["results"].append(
                {
                    "text": display_name,
                    "point": point,
                    "bbox": bbox,
                    "id": "geocode-" + str(geocode_id),
                }
            )

        return JsonResponse(json)

    def convert_geojson_to_shapefile(self, request, *args, **kwargs):
        """
        AJAX handler that converts GeoJSON data into a shapefile for download.
            Credit to: https://github.com/TipsForGIS-zz/geoJSONToShpFile/blob/master/geoJ.py

        .. important::

            This method requires the `pyshp` library to be installed. Starting with Tethys 5.0 or if you are using `micro-tethys-platform`, you will need to install `django-json-widget` using conda or pip as follows:

        .. code-block:: bash

            # conda: conda-forge channel strongly recommended
            conda install -c conda-forge pyshp

            # pip
            pip install pyshp

        **Don't Forget**: If you end up using this method in your app, add `pyshp` as a requirement to your `install.yml`.

        Args:
            request(HttpRequest): The request.

        Returns:
            JsonResponse: success.
        """
        json_data = json.loads(request.POST.get("data", ""))
        layer_id = request.POST.get("id", "0")
        json_type = json_data["features"][0]["geometry"]["type"]
        shape_types = {
            "Polygon": shapefile.POLYGON,
            "Point": shapefile.POINT,
            "LineString": shapefile.POLYLINE,
        }

        if json_type not in shape_types:
            raise ValueError(
                "Only GeoJson of the following types are supported: Polygon, Point, or LineString"
            )

        with tempfile.TemporaryDirectory() as tmpdir:
            shp_base = layer_id + "_" + json_type
            shp_file = str(Path(tmpdir) / shp_base)

            with shapefile.Writer(shp_file, shape_types[json_type]) as shpfile_obj:
                shpfile_obj.autoBalance = 1

                # Define fields from geojson properties
                columns_list = json_data["features"][0]["properties"].keys()
                for col in columns_list:
                    shpfile_obj.field(str(col), "C", "50")

                # Extract geometry and attributes from geojson
                geometries = list()
                attributes = list()
                for feature in json_data["features"]:
                    if feature["geometry"]["type"] == json_type:
                        geometries.append(feature["geometry"]["coordinates"])
                    attributes_per_feature = list()
                    for attribute_feature in columns_list:
                        attributes_per_feature.append(
                            str(feature["properties"][str(attribute_feature)])
                        )
                    attributes.append(attributes_per_feature)

                # Write geometry
                for geo in geometries:
                    if json_type == "Polygon":
                        shpfile_obj.poly(polys=geo)
                    elif json_type == "Point":
                        shpfile_obj.point(geo[0], geo[1])
                    elif json_type == "LineString":
                        shpfile_obj.line(lines=[geo])

                # Add records
                for attr in attributes:
                    shpfile_obj.record(*attr)

            # write projection file
            with open(shp_file + ".prj", "w") as prj_file:
                prj_str = (
                    'GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],'
                    'PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]]'
                )
                prj_file.write(prj_str)

            in_memory = BytesIO()
            shp_file_ext = ["prj", "shp", "dbf", "shx"]

            with ZipFile(in_memory, "w") as my_zip:
                for ext in shp_file_ext:
                    my_zip.write(f"{shp_file}.{ext}", f"{shp_base}.{ext}")

        response = HttpResponse(content_type="application/zip")
        response["Content-Disposition"] = f'attachment; filename="{shp_base}.zip"'

        in_memory.seek(0)
        response.write(in_memory.read())
        return response

    # Utilities ------------------------------------------------------------- #
    @classmethod
    def get_wms_endpoint(cls, public=True):
        """
        Get the public wms endpoint for GeoServer.
        """
        wms_endpoint = (
            cls.sds_setting.public_endpoint if public else cls.sds_setting.endpoint
        )
        wms_endpoint = wms_endpoint.replace("rest", "wms")

        # Add trailing slash for consistency.
        if wms_endpoint[-1] != "/":
            wms_endpoint += "/"
        return wms_endpoint
