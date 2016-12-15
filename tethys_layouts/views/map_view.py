"""
********************************************************************************
* Name: tethys_layouts/views/map_view.py
* Author: Nathan Swain
* Created On: December 10, 2016
* Copyright: (c) Nathan Swain 2016
* License: BSD 2-Clause
********************************************************************************
"""
from tethys_layouts.views.base import TethysLayoutController
from tethys_sdk.gizmos import MapView, MVView


class MapViewLayoutController(TethysLayoutController):
    """
    A Class-Based Controller for handling the MapViewLayout.
    """
    template_name = "tethys_layouts/map_view.html"

    def construct_map_view(self):
        """
        Construct and return the MapView gizmo used by the MapViewLayout
        """
        view_options = MVView(
            projection='EPSG:4326',
            center=[-100, 40],
            zoom=3.5,
            maxZoom=18,
            minZoom=2
        )

        map_view_gizmo = MapView(
            height='600px',
            width='100%',
            controls=['ZoomSlider', 'Rotate', 'FullScreen',
                      {'MousePosition': {'projection': 'EPSG:4326'}},
                      {'ZoomToExtent': {'projection': 'EPSG:4326', 'extent': [-130, 22, -65, 54]}}],
            layers=[],
            view=view_options,
            basemap='OpenStreetMap',
            legend=True
        )
        return map_view_gizmo

    def get(self, request, *args, **kwargs):
        """
        Handle Get Requests
        """
        context = self.get_context_data(**kwargs)
        context['map_view_gizmo'] = self.construct_map_view()
        return self.render_to_response(context)
