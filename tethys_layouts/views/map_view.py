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

    def build_layers(self, request, *args, **kwargs):
        """
        Build and return the MVLayers for then underlying MapView Gizmo.
        """
        map_layers = []
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

        geojson_layer = MVLayer(source='GeoJSON',
                                options=geojson_object,
                                legend_title='Test GeoJSON',
                                legend_extent=[-46.7, -48.5, 74, 59],
                                legend_classes=[
                                    MVLegendClass('polygon', 'Polygons', fill='rgba(255,255,255,0.8)',
                                                  stroke='#3d9dcd'),
                                    MVLegendClass('line', 'Lines', stroke='#3d9dcd')
                                ])

        map_layers.append(geojson_layer)

        # Tiled ArcGIS REST Layer
        arc_gis_layer = MVLayer(source='TileArcGISRest',
                                options={'url': 'http://sampleserver1.arcgisonline.com/ArcGIS/rest/services/' +
                                                'Specialty/ESRI_StateCityHighway_USA/MapServer'},
                                legend_title='ESRI USA Highway',
                                legend_extent=[-173, 17, -65, 72])

        map_layers.append(arc_gis_layer)
        return map_layers

    def build_mvdraw(self, request, *args, **kwargs):
        """
        Build and return MVDraw for the underlying MapView Gizmo.
        """
        mvdraw = MVDraw(
            controls=['Modify', 'Delete', 'Move', 'Point', 'LineString', 'Polygon', 'Box'],
            initial='Point',
            output_format='WKT'
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
            controls=['ZoomSlider', 'Rotate', 'FullScreen',
                      {'MousePosition': {'projection': 'EPSG:4326'}},
                      {'ZoomToExtent': {'projection': 'EPSG:4326', 'extent': [-130, 22, -65, 54]}}],
            layers=self.build_layers(request, args, kwargs),
            view=self.build_mvview(request, args, kwargs),
            basemap='OpenStreetMap',
            draw=self.build_mvdraw(request, args, kwargs),
            legend=self.legend
        )
        return map_view_gizmo

    def on_save(self, request, *args, **kwargs):
        """
        Handle a save event from the map.
        """
        success = True
        # Do nothing by default
        return success

    def get(self, request, *args, **kwargs):
        """
        Handle Get Requests
        """
        # Get context
        context = self.get_context_data(**kwargs)

        request_type = request.GET.get('type', None)

        if request_type == 'on-save':
            success = self.on_save(request, args, kwargs)
            return JsonResponse({'success': success})
        elif request_type == 'on-delete':
            # do stuff
            return JsonResponse({'success': True})

        # Add to context
        context['map_view_gizmo'] = self.build_map_view(request, args, kwargs)
        return self.render_to_response(context)
