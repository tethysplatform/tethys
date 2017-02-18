"""
********************************************************************************
* Name: tethys_layouts/views/map_view.py
* Author: Nathan Swain
* Created On: December 10, 2016
* Copyright: (c) Nathan Swain 2016
* License: BSD 2-Clause
********************************************************************************
"""
from django.http import JsonResponse
from tethys_layouts.views.base import TethysLayoutController
from tethys_sdk.gizmos import MapView, MVView, MVDraw, MVLayer, MVLegendClass


class MapViewLayoutController(TethysLayoutController):
    """
    A Class-Based Controller for handling the MapViewLayout.
    """
    # These properties can be overridden by arguments of the same name passed to the
    # constructor of the class in the URL map
    template_name = "tethys_layouts/map_view.html"

    # Legend
    legend = True

    # MVView
    projection = 'EPSG:4326'
    initial_center = [-100, 40]
    min_zoom = 2
    max_zoom = 18
    initial_zoom = 3.5
    basemap = 'OpenStreetMap'
    input_data_format = 'GeoJSON'

    def build_controls(self, request, *args, **kwargs):
        """
        Build and return the list of controls that are enabled on the map.
        """
        default_controls = ['ZoomSlider', 'Rotate']
        return default_controls

    def build_layers(self, request, *args, **kwargs):
        """
        Build and return the MVLayers for then underlying MapView Gizmo.
        """
        return []

    def build_mvdraw(self, request, *args, **kwargs):
        """
        Build and return MVDraw for the underlying MapView Gizmo.
        """
        mvdraw = MVDraw(
            controls=['Modify', 'Delete', 'Move', 'Point', 'LineString', 'Polygon', 'Box'],
            initial='Point',
            output_format=self.input_data_format
        )
        return mvdraw

    def build_mvview(self, request, *args, **kwargs):
        """
        Build and return MVView for the underlying MapView Gizmo.
        """
        mvview = MVView(
            projection=self.projection,
            center=self.initial_center,
            zoom=self.initial_zoom,
            maxZoom=self.max_zoom,
            minZoom=self.min_zoom
        )
        return mvview

    def build_map_view(self, request, *args, **kwargs):
        """
        Build and return the underlying MapView Gizmo used by the MapViewLayout
        """
        map_view_gizmo = MapView(
            height='600px',
            width='100%',
            controls=self.build_controls(request, args, kwargs),
            layers=self.build_layers(request, args, kwargs),
            view=self.build_mvview(request, args, kwargs),
            basemap=self.basemap,
            draw=self.build_mvdraw(request, args, kwargs),
            legend=self.legend
        )
        return map_view_gizmo

    def on_save(self, request, *args, **kwargs):
        """
        Handle a save event from the map.
        """
        return False

    def get(self, request, *args, **kwargs):
        """
        Handle Get Requests
        """
        # Get context
        context = self.get_context_data(**kwargs)

        # Add to context
        context['map_view_gizmo'] = self.build_map_view(request, args, kwargs)
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        """
        Handle Post Requests
        """
        # Get request type
        event = request.POST.get('event', None)

        if event == 'on-save':
            success = self.on_save(request, args, kwargs)
            return JsonResponse({'success': success})

        return JsonResponse({'success': False})
